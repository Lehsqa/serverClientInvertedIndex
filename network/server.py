import multiprocessing
import socket
import logging
import re
import ast
from inverted_index.rw_json import Json


def lookup_query(word: str, file=None):
    data = Json.read()
    word = re.sub(r'[^\w\s]', '', word).lower()
    count = 0

    if word in data:
        if file is None:
            for i in data[word]:
                count = count + ast.literal_eval(i).get("freq")
        else:
            for i in data[word]:
                data = ast.literal_eval(i)
                if data.get("doc_id")[0] == file:
                    count = count + data.get("freq")
                else:
                    continue
        return str(count)
    else:
        return "0"


def file_list(word: str):
    data = Json.read()
    word = re.sub(r'[^\w\s]', '', word).lower()
    lst = list()

    if word in data:
        for i in data[word]:
            file = ast.literal_eval(i).get("doc_id")[0]
            if file not in lst:
                lst.append(file)
            else:
                continue
        return str(lst)
    else:
        return "Null"


def handle(connection, address: str, queue):
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(f"process-{(address,)}")
    try:
        logger.debug(f"Connected {connection} at {address}")
        while True:
            data = connection.recv(1024).decode("utf-8")
            if data[:13] == "upload_file: ":
                queue.put(data[13:])
                logger.debug(f"Received command '{data[:11]}' with data '{data[13:]}'")
                connection.sendall(bytes("File was upload", 'utf-8'))
                logger.debug("Sent data")
            elif data[:10] == "find_all: ":
                logger.debug(f"Received command '{data[:8]}' with data '{data[10:]}'")
                connection.sendall(bytes("All: " + lookup_query(data[10:]), 'utf-8'))
                logger.debug("Sent data")
            elif data[:10] == "find_one: ":
                logger.debug(f"Received command '{data[:8]}' with data '{data[10:]}'")
                new_data = data[10:].split(' ')
                connection.sendall(bytes(new_data[1] + ": " + lookup_query(new_data[0], new_data[1]), 'utf-8'))
                logger.debug("Sent data")
            elif data[:12] == "where_find: ":
                logger.debug(f"Received command '{data[:10]}' with data '{data[12:]}'")
                connection.sendall(bytes(file_list(data[12:]), 'utf-8'))
                logger.debug("Sent data")
            elif data == "close":
                logger.debug("Socket closed remotely")
                break
            else:
                logger.debug("Received wrong command")
                connection.sendall(bytes("Wrong command, try again", 'utf-8'))
                logger.debug("Sent data")
    except:
        logger.exception("Problem handling request")
    finally:
        logger.debug("Closing socket")
        connection.close()


class Server(object):
    def __init__(self, hostname: str, port: int):
        self.logger = logging.getLogger("server")
        self.hostname = hostname
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, queue):
        self.logger.debug("listening")
        self.socket.bind((self.hostname, self.port))
        self.socket.listen()

        while True:
            conn, address = self.socket.accept()
            self.logger.debug("Got connection")
            process = multiprocessing.Process(target=handle, args=(conn, address, queue))
            process.daemon = True
            process.start()
            self.logger.debug("Started process %r", process)


def server(queue):
    logging.basicConfig(level=logging.DEBUG)
    server = Server("0.0.0.0", 9000)
    try:
        logging.info("Listening")
        server.start(queue)
    except:
        logging.exception("Unexpected exception")
    finally:
        logging.info("Shutting down")
        for process in multiprocessing.active_children():
            logging.info("Shutting down process %r", process)
            process.terminate()
            process.join()
    logging.info("All done")
