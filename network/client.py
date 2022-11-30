import socket


class Client(object):
    def __init__(self, hostname: str, port: int):
        self.hostname = hostname
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.socket.connect((self.hostname, self.port))

        while True:
            data = input()
            self.socket.sendall(bytes(data, "utf-8"))
            if data == "close":
                self.socket.close()
                break
            result = self.socket.recv(1024).decode('utf-8')
            print(result)


if __name__ == "__main__":
    client = Client("localhost", 9000)
    client.start()