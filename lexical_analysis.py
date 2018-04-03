from automaton import ParserAutomaton
from token import TokenCollection

src_name = 'script'
src_path = src_name + '.simple'
lex_path1 = src_name + '_on_the_fly.lex'
lex_path2 = src_name + '_together.lex'
set_path = src_name + '.set'
log_path = src_name + '.log'
key_path = 'keywords.txt'

parser = ParserAutomaton()

with open(key_path) as fk:
    keywords = ''.join(fk.readlines()).split()

collection = TokenCollection(keywords, lex_path1, set_path, write_on_the_fly = True)

with open(src_path) as fi, open(log_path, 'w') as fl:
    for line in fi.readlines():
        for ch in line[:-1] + ' ': # replace the last \n character with space
            final = parser.process(ch)
            print('current char = %s, final = %s' % (ch, final))
            if final:
                fl.writelines(['(%s,%s)-->%s, current-lex=%s\n' % tup for tup in parser.logs])
                fl.write('----------------------%s----------------------\n\n' % parser.current_lex)
                if parser.current_state == 'illegal':
                    raise KeyError('illegal state encountered')
                collection.append(parser.current_lex, parser.current_state)
                # TODO: Roll Back
                parser.start_over()
                parser.process(ch)

collection.write_list(lex_path2)
collection.write_set()