import datetime


class TokenCollection:
    def __init__(self, keywords, lex_path, set_path, write_on_the_fly=False):
        self.keywords = keywords
        self.type2ID = {
            'constant_end': 10,
            'str_end': 20,
            'symbol_end': 30,
            'comment_end': 40,
            'identifier_end': 50,
            'keyword_end': 60,
        }
        self.ID2type = {self.type2ID[key]: key for key in self.type2ID}
        self.set = {self.type2ID[key]: [] for key in self.type2ID}
        self.set[self.type2ID['keyword_end']] = self.keywords
        self.list = []
        self.write_on_the_fly = write_on_the_fly
        self.lex_path = lex_path
        self.set_path = set_path
        if self.write_on_the_fly:
            with open(self.lex_path, 'w'), open(self.set_path, 'w'):
                pass  # wipe the files

    def append(self, token, accepted_state):
        if accepted_state == 'identifier_end' and token in self.keywords:
            accepted_state = 'keyword_end'
        ID = self.type2ID[accepted_state]
        l = self.set[ID]
        if token not in l: l.append(token)
        self.list.append((ID, l.index(token)))
        if self.write_on_the_fly:
            self.__write_latest()

    def write_set(self, set_path=None):
        set_path = set_path if set_path else self.set_path
        with open(set_path, 'w') as fo:
            for ID in self.set:
                fo.write('%d: %s\n' % (ID, self.ID2type[ID]))
                for index, entry in enumerate(self.set[ID]):
                    fo.write('    %d: %s\n' % (index, entry))

    def __write_latest(self, lex_path=None):
        lex_path = lex_path if lex_path else self.lex_path
        with open(lex_path, 'a') as fo:
            fo.write('{} <{},{}>\n'.format(datetime.datetime.now(), *self.list[-1]))

    def write_list(self, lex_path=None):
        lex_path = lex_path if lex_path else self.lex_path
        with open(lex_path, 'w') as fo:
            fo.writelines(["<%d,%d>\n" % _ for _ in self.list])
