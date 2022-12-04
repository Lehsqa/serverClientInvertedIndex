from json import load, dump, decoder


class Json:
    @staticmethod
    def read(read_lock):
        with read_lock:
            with open("inverted_index/buffer", 'r', encoding='UTF-8') as infile:
                try:
                    return load(infile)
                except decoder.JSONDecodeError:
                    return {}

    @classmethod
    def write(cls, queue, read_lock, write_lock):
        with write_lock:
            while True:
                data = queue.get()

                if data == 'kill':
                    break

                old_data = cls.read(read_lock)

                with open("inverted_index/buffer", 'w') as outfile:
                    for (key, value) in data.items():
                        if key not in old_data:
                            old_data[key] = value
                        else:
                            old_data[key] = old_data[key] + value
                    dump(old_data, outfile)
                    outfile.flush()
