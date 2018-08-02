

class Foo:
    def __new__(cls, *args, **kwargs):
        print('hgoe')
        return super().__new__(cls)

    def __init__(self):
        print("hoge")

class Bar(Foo):
    def __init__(self):
        print("piyo")

Bar()
