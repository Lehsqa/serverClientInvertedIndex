from inverted_index.inverted_index import generate_and_add_data
from network.server import server
from multiprocessing import Queue, Process
from time import sleep


def test(queue):
    queue.put("doc1")
    print("Doc1")
    # sleep(1)
    queue.put("doc2")
    print("Doc2")
    # sleep(1)
    queue.put("doc3")
    print("Doc3")
    # sleep(1)
    queue.put("kill")
    print("kill")


if __name__ == "__main__":
    queue_doc = Queue()

    p0 = Process(target=generate_and_add_data, args=(queue_doc,))
    p0.start()

    sleep(1)

    # p1 = Process(target=test, args=(queue_doc,))
    # p1.start()
    server(queue_doc)

    p0.join()
    # p1.join()
