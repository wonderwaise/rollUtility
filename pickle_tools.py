from pickle import dump, load


class Database:
    @staticmethod
    def save(data):
        with open('db.pickle', 'wb') as f:
            dump(data, f)

    @staticmethod
    def load():
        try:
            with open('db.pickle', 'rb') as f:
                return load(f)
        except FileNotFoundError:
            return []