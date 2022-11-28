class File:
    @staticmethod
    def read(name):
        with open("documents/" + name, 'r', encoding='UTF-8') as f:
            return {'id': name, 'data': f.read()}

    @staticmethod
    def write():
        pass
