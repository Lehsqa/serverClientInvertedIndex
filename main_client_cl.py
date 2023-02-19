from gui.comand_line import queue_commands, add_command
from network.client import Client
from threading import Thread


if __name__ == "__main__":
    client = Client("localhost", 9000, queue_commands)
    t = Thread(target=client.start, args=(None,))

    t.start()
    add_command()
    t.join()
