import queue

queue_commands = queue.Queue()


def add_command():
    while True:
        command = input()
        queue_commands.put(command)
        if command == 'close':
            break
