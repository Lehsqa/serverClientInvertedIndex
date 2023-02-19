import socket
from tkinter import END


class Client(object):
    def __init__(self, hostname: str, port: int, queue):
        self.hostname = hostname
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.queue = queue

    def start(self, text):
        self.socket.connect((self.hostname, self.port))

        while True:
            data = self.queue.get()
            self.socket.sendall(bytes(data, "utf-8"))
            if data == "close":
                self.socket.close()
                break
            result = self.socket.recv(1024).decode('utf-8')
            if text is None:
                print(result + '\n')
            else:
                text.insert(END, data + '\n')
                text.insert(END, result + '\n\n')
