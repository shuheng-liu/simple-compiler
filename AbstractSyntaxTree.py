class Node:
    def __init__(self, type: str, children: list = None, leaf=None):
        self.type = type
        assert isinstance(children, list) or children is None, "illegal when constructing {}".format(type)
        self.children = children if children else list()
        self.leaf = leaf

    def traverse(self, indent=0):
        padding = ' ' * indent
        block = ' ' * 4
        print(padding, "PRODUCTION: ", self.type, "{")
        if self.children or self.leaf:
            print(padding+block, "LEAF:", self.leaf)
            # print()
            # print(padding+block, "children:")
            # print()

            if self.children is not None:
                for child in self.children:
                    if child is None:
                        continue
                    child.traverse(indent=indent + 4)
                    print()

        print(padding, "}")


if __name__ == "__main__":
    n1 = Node("type1", leaf="n1")
    n2 = Node("type2", leaf="n2")
    n3 = Node("type3", leaf="n3")
    n4 = Node("type4", leaf="n4")
    n5 = Node("type5", leaf="n5")
    n6 = Node("type6", leaf="n6")
    n7 = Node("type7", leaf="n7")
    n8 = Node("type8", leaf="n8")
    n9 = Node("type9", leaf="n9")

    n123 = Node("type123", children=[n1, n2, n3], leaf="n123")
    n456 = Node("type456", children=[n4, n5, n6], leaf="n456")
    n789 = Node("type789", children=[n7, n8, n9], leaf="n789")

    n1_9 = Node("type1_9", children=[n123, n456, n789], leaf="n1_9")

    n1_9.traverse()
