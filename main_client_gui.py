from gui.gui import root, text, queue_commands
from network.client import Client
from threading import Thread


if __name__ == "__main__":
    client = Client("localhost", 9000, queue_commands)
    t = Thread(target=client.start, args=(text,))

    t.start()
    root.mainloop()
    t.join()
