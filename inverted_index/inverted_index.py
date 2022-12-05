import re
from multiprocessing import Manager, Pool
from json import dumps
from itertools import repeat
from inverted_index.rw_json import Json
from inverted_index.rw_file import File
from config import STOP_WORDS_INVERTED_INDEX, THREAD_COUNT_INVERTED_INDEX


class Value:
    def __init__(self, doc_id: str, freq: int):
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

    def index_document(self, doc: dict, queue):
        value_dict = dict()
        terms = re.sub(r'[^\w\s]', '', doc['data']).lower().split(' ')

        for term in terms:
            if term in STOP_WORDS_INVERTED_INDEX:
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


def to_divine(doc_id: str, data: str, count: int):
    new_data = data.replace('.', '').split(' ')

    new_length = len(new_data)
    if new_length < count:
        count = new_length

    length = int(new_length/count)

    return [{'id': doc_id, 'data': " ".join(new_data[length*i:length*(i+1)])
            if i != count-1 else " ".join(new_data[length*i:])} for i in range(count)], count


def generate_and_add_data(queue_doc, write_lock):
    queue_adding = Manager().Queue()

    index = InvertedIndex()
    db = Json()
    file = File()

    while True:
        thread_count = THREAD_COUNT_INVERTED_INDEX
        doc_name = queue_doc.get()
        if doc_name == 'kill':
            break
        doc = file.read(doc_name)

        if thread_count == 1:
            divide_list = [{'id': doc["id"], 'data': doc["data"].replace('.', '')}]
        else:
            divide_list, thread_count = to_divine(doc["id"], doc["data"], thread_count)

        with Pool(thread_count) as p:
            p.starmap(index.index_document, zip(divide_list, repeat(queue_adding)))

        first_json = queue_adding.get()
        while thread_count - 1 != 0:
            next_json = queue_adding.get()
            for (key, value) in next_json.items():
                if key not in first_json:
                    first_json[key] = value
                else:
                    first_json[key] = first_json[key] + value
            thread_count = thread_count - 1
        db.write(first_json, write_lock)

        del first_json
        del divide_list
        del doc
