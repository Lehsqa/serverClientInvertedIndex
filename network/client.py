import socket

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 9000))

    while True:
        data = input()
        sock.sendall(bytes(data, "utf-8"))
        if data == "kill":
            sock.close()
            break
        result = sock.recv(1024)
        print(result)
