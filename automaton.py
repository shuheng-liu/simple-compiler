class Automaton():
    def __init__(self):
        self.states = {'initial': 0}
        self.final_states = set()
        self.transition = {}
        self.start_over()

        self.Sigma = 'abcdefghijklmnopqrstuvwxyz'
        self.Sigma += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.Sigma += '0123456789.'
        self.Sigma += '+-*/,;:=_"\'\\<>{}()[]!?@#$%^&* \t'
        self.Sigma = set(self.Sigma)

    def append_state(self, state, final=None):
        if state in self.states:
            raise KeyError('state already existent')
        self.states[state] = len(self.states)
        if final: self.final_states.add(state)

    def append_transition(self, state1, state2, chars):
        assert state1 in self.states, '%s not in states' % state1
        assert state2 in self.states, '%s not in states' % state2
        for ch in chars:
            self.transition[(state1, ch)] = state2

    def start_over(self):
        self.current_state = 'initial'
        self.current_lex = ''
        self.logs = []

    def process(self, ch):
        state = self.current_state
        new_state = self.transition[(state, ch)]
        if new_state not in self.final_states and new_state != 'initial':
            self.current_lex += ch
        self.current_state = new_state
        self.logs.append((state, ch, new_state, self.current_lex))
        return new_state in self.final_states

    def check_mapping(self):
        flag = True
        for state in self.states:
            for sigma in self.Sigma:
                if (state, sigma) not in self.transition:
                    print('transition mapping: (%s, %s) |--> new_state does not exist' % (state, sigma))
                    flag = False
        return flag


class ParserAutomaton(Automaton):
    def __init__(self):
        super().__init__()
        self.__append_states()
        self.__append_transitions()
        assert self.check_mapping()  # check that transition mapping: Q x Sigma -> Q is fully defined

    def __append_states(self):
        self.append_state('identifier')
        self.append_state('constant without dot')
        self.append_state('constant with dot')
        self.append_state("'")
        self.append_state("'str")
        self.append_state("'str'")  # pre-'end'

        # if starting with a single symbol
        self.append_state('<')
        self.append_state('>')
        self.append_state('=')
        self.append_state('.')
        self.append_state(',')
        self.append_state(':')
        self.append_state('/')
        self.append_state(';')  # pre-'end'
        self.append_state('+')  # pre-'end'
        self.append_state('-')  # pre-'end'
        self.append_state('*')
        self.append_state('(')  # pre-'end'
        self.append_state(')')  # pre-'end'
        self.append_state('[')  # pre-'end'
        self.append_state(']')  # pre-'end'
        self.append_state('{')  # pre-'end'
        self.append_state('}')  # pre-'end'

        # if starting with two symbols
        self.append_state('<=')  # pre-'end'
        self.append_state('<>')  # pre-'end'
        self.append_state('>=')  # pre-'end'
        self.append_state('==')  # pre-'end'
        self.append_state(':=')  # pre-'end'
        self.append_state('/*')  # pre-'end'
        self.append_state('//')  # pre-'end'
        self.append_state('**')  # pre-'end'

        self.append_state('illegal', final=True)
        self.append_state('identifier_end', final=True)
        self.append_state('constant_end', final=True)
        self.append_state('str_end', final=True)
        self.append_state('symbol_end', final=True)
        self.append_state('comment_end', final=True)

    def __append_transitions(self):
        alphabetic = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        digit = set('1234567890')
        digit_dot = set('1234567890.')

        alphabetic_underscore = alphabetic.copy()
        alphabetic_underscore.add('_')

        alphanumeric = alphabetic.copy()
        alphanumeric.update('1234567890')

        alphanumeric_underscore = alphanumeric.copy()
        alphabetic_underscore.add('_')

        self.append_transition('initial', 'identifier', alphabetic_underscore)
        self.append_transition('initial', 'initial', set(' \t'))
        self.append_transition('initial', 'constant without dot', digit)
        self.append_transition('initial', 'constant with dot', set('.'))
        self.append_transition('initial', "'", set("'"))
        self.append_transition('initial', '<', set('<'))
        self.append_transition('initial', '>', set('>'))
        self.append_transition('initial', '=', set('='))
        self.append_transition('initial', '.', set('.'))
        self.append_transition('initial', ',', set(','))
        self.append_transition('initial', ':', set(':'))
        self.append_transition('initial', '/', set('/'))
        self.append_transition('initial', ';', set(';'))
        self.append_transition('initial', '+', set('+'))
        self.append_transition('initial', '-', set('-'))
        self.append_transition('initial', '*', set('*'))
        self.append_transition('initial', '(', set('('))
        self.append_transition('initial', ')', set(')'))
        self.append_transition('initial', '[', set('['))
        self.append_transition('initial', ']', set(']'))
        self.append_transition('initial', '{', set('{'))
        self.append_transition('initial', '}', set('}'))
        self.append_transition('initial', 'illegal', self.Sigma - alphanumeric - set("_'<>=,.:/;+-*()[]{} \t"))

        self.append_transition('identifier', 'identifier', alphanumeric_underscore)
        self.append_transition('identifier', 'identifier_end', self.Sigma - alphanumeric_underscore)

        self.append_transition('constant without dot', 'constant without dot', digit)
        self.append_transition('constant without dot', 'constant with dot', set('.'))
        self.append_transition('constant without dot', 'illegal', alphabetic_underscore)
        self.append_transition('constant without dot', 'constant_end', self.Sigma - digit_dot - alphanumeric_underscore)
        self.append_transition('.', 'constant with dot', digit)
        self.append_transition('constant with dot', 'constant with dot', digit)
        self.append_transition('constant with dot', 'illegal', alphabetic_underscore | set('.'))
        self.append_transition('constant with dot', 'constant_end', self.Sigma - digit_dot - alphanumeric_underscore)

        self.append_transition("'", "'str", self.Sigma - set("'"))
        self.append_transition("'", "'str'", set("'"))
        self.append_transition("'str", "'str", self.Sigma - set("'"))
        self.append_transition("'str", "'str'", set("'"))
        self.append_transition("'str'", 'str_end', self.Sigma)

        self.append_transition('<', '<=', set('='))
        self.append_transition('<', '<>', set('>'))
        self.append_transition('<', 'symbol_end', self.Sigma - set('=>'))
        self.append_transition('>', '>=', set('>'))
        self.append_transition('>', 'symbol_end', self.Sigma - set('>'))
        self.append_transition('=', '==', set('='))
        self.append_transition('=', 'symbol_end', self.Sigma - set('='))
        self.append_transition(':', ':=', set('='))
        self.append_transition(':', 'symbol_end', self.Sigma - set('='))
        self.append_transition('/', '//', set('/'))
        self.append_transition('/', '/*', set('*'))
        self.append_transition('/', 'symbol_end', self.Sigma - set('/*'))
        self.append_transition('*', '**', set('*'))
        self.append_transition('*', 'symbol_end', self.Sigma - set('*'))
        self.append_transition('.', 'symbol_end', self.Sigma - digit)

        self.append_transition(',', 'symbol_end', self.Sigma)
        self.append_transition(';', 'symbol_end', self.Sigma)
        self.append_transition('+', 'symbol_end', self.Sigma)
        self.append_transition('-', 'symbol_end', self.Sigma)
        self.append_transition('(', 'symbol_end', self.Sigma)
        self.append_transition(')', 'symbol_end', self.Sigma)
        self.append_transition('[', 'symbol_end', self.Sigma)
        self.append_transition(']', 'symbol_end', self.Sigma)
        self.append_transition('{', 'symbol_end', self.Sigma)
        self.append_transition('}', 'symbol_end', self.Sigma)
        self.append_transition('<=', 'symbol_end', self.Sigma)
        self.append_transition('<>', 'symbol_end', self.Sigma)
        self.append_transition('>=', 'symbol_end', self.Sigma)
        self.append_transition('==', 'symbol_end', self.Sigma)
        self.append_transition(':=', 'symbol_end', self.Sigma)
        self.append_transition('/*', 'symbol_end', self.Sigma)
        self.append_transition('//', 'symbol_end', self.Sigma)
        self.append_transition('**', 'symbol_end', self.Sigma)

        self.append_transition('illegal', 'illegal', self.Sigma)
        self.append_transition('identifier_end', 'identifier_end', self.Sigma)
        self.append_transition('constant_end', 'constant_end', self.Sigma)
        self.append_transition('str_end', 'str_end', self.Sigma)
        self.append_transition('symbol_end', 'symbol_end', self.Sigma)
        self.append_transition('comment_end', 'comment_end', self.Sigma)


if __name__ == "__main__":
    parser = ParserAutomaton()
    print(parser.Sigma)
    print(parser.states)
