from inverted_index.inverted_index import generate_and_add_data
from multiprocessing import Queue

if __name__ == "__main__":
    queue_doc = Queue()

    while True:
        data = input("Enter the name of document: ")
        if data == 'kill':
            queue_doc.put(data)
            break
        queue_doc.put(data)

    generate_and_add_data(queue_doc)
