class Node:
    def __init__(self, type: str, children: list = None, leaf=None):
        self.type = type
        self.children = children if children else list()
        self.leaf = leaf

    def traverse(self):
        pass
