from inverted_index.inverted_index import generate_and_add_data
from network.server import server
from multiprocessing import Queue, Process, RLock
from config import THREAD_COUNT_FILES
from time import sleep, time


write_lock = RLock()


def test(queue):
    queue.put("doc1")
    print("Doc1")
    # sleep(1)
    queue.put("doc2")
    print("Doc2")
    # sleep(1)
    # queue.put("doc3")
    # print("Doc3")
    # sleep(1)
    queue.put("kill")
    # queue.put("kill")
    print("kill")


def new_test(queue, count):
    for i in range(100):
        queue.put(f"doc{i+1}")
    for _ in range(count):
        queue.put("kill")


if __name__ == "__main__":
    queue_doc = Queue()
    process_list = list()

    # test(queue_doc)
    # new_test(queue_doc, THREAD_COUNT_FILES)

    # start = time()
    for _ in range(THREAD_COUNT_FILES):
        p = Process(target=generate_and_add_data, args=(queue_doc, write_lock))
        p.start()
        process_list.append(p)

    sleep(1)

    server(queue_doc)

    for p in process_list:
        p.join()
    # print("Time: " + str(time() - start))
