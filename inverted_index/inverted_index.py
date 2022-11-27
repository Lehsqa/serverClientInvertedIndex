import re
import multiprocessing as mp
from inverted_index.rw_json import Json
from json import dumps
from itertools import repeat

STOP_WORDS = ['of', 'the', 'a', 'in', 'on', 'at', 'from', 'an', 'to', 'into', 'with', 'that', 'what', 'where', 'why',
              'when']

THREAD_COUNT = 4


def to_divine(doc_id, data, count):
    new_data = data.replace('.', '').split(' ')

    new_length = len(new_data)
    if new_length < count:
        count = new_length

    length = int(new_length/count)

    return [{'id': doc_id + f"/{i+1}", 'data': " ".join(new_data[length*i:length*(i+1)])
            if i != count-1 else " ".join(new_data[length*i:])} for i in range(count)], count


class ReadFiles:
    def __init__(self, name):
        self.name = name
        self.data = ""

    def read(self):
        with open("documents/" + self.name, 'r', encoding='UTF-8') as f:
            self.data = f.read()

        return {'id': self.name, 'data': self.data}


class Value:
    def __init__(self, doc_id, freq):
        self.doc_id = doc_id,
        self.freq = freq

    def __repr__(self):
        return str(self.__dict__)

    def to_json(self):
        return dumps(self, default=lambda o: o.__dict__, sort_keys=True)


class InvertedIndex:
    def __init__(self):
        self.index = dict()

    def __repr__(self):
        return str(self.__dict__)

    def index_document(self, doc, queue):
        value_dict = dict()
        terms = re.sub(r'[^\w\s]', '', doc['data']).lower().split(' ')

        for term in terms:
            if term in STOP_WORDS:
                continue

            if term in value_dict:
                term_freq = value_dict[term].freq
            else:
                term_freq = 0

            value_dict[term] = Value(doc['id'], term_freq + 1)

        for (key, value) in value_dict.items():
            if key not in self.index:
                self.index.update({key: [value.to_json()]})
            else:
                self.index.update({key: self.index[key] + [value.to_json()]})

        queue.put(self.index)

    def lookup_query(self, query):
        data = Json.read_mp()

        if query in data:
            return data[query]
        else:
            return {}


def process(queue_doc, queue_final):
    index = InvertedIndex()
    queue_adding = mp.Manager().Queue()

    while True:
        thread_count = THREAD_COUNT

        doc_name = queue_doc.get()
        if doc_name == 'kill':
            break
        doc = ReadFiles(doc_name).read()

        divide_list, thread_count = to_divine(doc["id"], doc["data"], thread_count)

        with mp.Pool(thread_count) as p:
            p.starmap(index.index_document, zip(divide_list, repeat(queue_adding)))

        f_json = queue_adding.get()

        while thread_count - 1 != 0:
            new_json = queue_adding.get()

            for (key, value) in new_json.items():
                if key not in f_json:
                    f_json[key] = value
                else:
                    f_json[key] = f_json[key] + value

            del new_json
            thread_count = thread_count - 1

        queue_final.put(f_json)


def generate_and_add_data(queue_doc):
    queue_final = mp.Manager().Queue()

    db = Json()

    watcher = mp.Process(target=db.add_mp, args=(queue_final,))
    watcher.start()

    generate_data = mp.Process(target=process, args=(queue_doc, queue_final))
    generate_data.start()

    generate_data.join()
    queue_final.put('kill')
    watcher.join()
