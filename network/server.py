import multiprocessing
import socket
import re
import ast
from inverted_index.rw_json import Json


def lookup_query(word):
    data = Json.read()
    word = re.sub(r'[^\w\s]', '', word).lower()
    count = 0

    if word in data:
        for i in data[word]:
            count = count + ast.literal_eval(i).get("freq")
        return str(count)
    else:
        return "0"


def handle(connection, address, queue):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("process-%r" % (address,))
    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            data = connection.recv(1024).decode("utf-8")
            if data[:5] == "find:":
                connection.sendall(bytes(lookup_query(data[5:]), 'utf-8'))
                continue
            queue.put(data)
            if data == "kill":
                logger.debug("Socket closed remotely")
                break
            logger.debug("Received data %r", data)
            connection.sendall(bytes(data, 'utf-8'))
            logger.debug("Sent data")
    except:
        logger.exception("Problem handling request")
    finally:
        logger.debug("Closing socket")
        connection.close()


class Server(object):
    def __init__(self, hostname, port):
        import logging
        self.logger = logging.getLogger("server")
        self.hostname = hostname
        self.port = port

    def start(self, queue):
        self.logger.debug("listening")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
    import logging
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
