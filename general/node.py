import threading, weakref, os, json

class Node:
    ctx = threading.local()
    by_id = weakref.WeakValueDictionary()
    def __init__(self, *nodes, **kwparams):
        self.data = kwparams
        self._nodes = nodes
        self.known_relations = set()
        self._init = False
    def init(self):
        self.inform()
        self._init = True
    def inform(self):
        for node in self._nodes:
            node.known_relations.add(self)
    def uninform(self):
        for node in self._nodes:
            node.known_relations.discard(self)
    def __del__(self):
        self.uninform()


    def id(node):
        return node.data.setdefault("id", id(node))
    @staticmethod
    def id2fn(id):
        return str(id) + '.json'
    def fn(node):
        return Node.id2fn(Node.id(node))
    @staticmethod
    def load(id):
        node = Node.by_id.get(id)
        if node is None:
            fn = Node.id2fn(id)
            with open(fn, 'rt') as file:
                nodes, data = json.load(file)
            node = Node(*nodes, **data)
            Node.by_id[id] = node
            node._nodes = tuple((Node.load(id) for id in node._nodes))
            node.init()
        return node
    #def reload(node):
    def save(node):
        id = Node.id(node)
        fn = Node.id2fn(id)
        with open(f'{fn}.new', 'wt') as file:
            json.dump(([Node.save(node) for node in node._nodes], node.data), file)
        os.rename(f'{fn}.new', fn)
        return id

    def __str__(self):
        if len(self._nodes) == 0:
            return self.data.get('name', self.id())
        else:
            return ' '.join((str(node) for node in self._nodes))

    def __getattr____(self, name):
        return self.data[name]
    def __getitem__(self, name):
        return self.data[name]

def named(name, *nodes, **kwparams):
    return Node(*nodes, name=name, **kwparams)

# we can define a logic via nodes
    # if a buy a yacht for 4$, how much money do i have?

if __name__ == '__main__':
    hello = named('hello')
    world = named('world')
    sentence = named('sentence', hello, world)
    sid = sentence.save() 
    print(sentence.fn())
    del sentence
    del hello
    del world
    sentence = Node.load(sid)
    print(sentence)
