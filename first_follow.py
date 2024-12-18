def first(grammar, symbol):
    first_set = set()
    symbol_set = {
        prod[1] for prod in grammar if prod[0] == symbol
    }
    for element in symbol_set:
        if element == 'epsilon':
            first_set.add(element)
        elif not element[0].isupper():
            first_set.add(element[0])
        else:
            first_set |= Production_rule_3(grammar, element)
    return first_set

def Production_rule_3(grammar, element):
    first_set = set()
    i = 0
    while i < len(element):
        first_i = first(grammar, element[i])
        first_set |= first_i.difference({'epsilon'})
        if 'epsilon' not in first_i:
            break
        i += 1
    return first_set

def follow(grammar, start_symbol, symbol):
    follow_set = set()
    if symbol == start_symbol:
        follow_set.add('$')
    for production in grammar:
        if symbol in production[1]:
            prodc = production[1]
            if symbol == prodc[-1]:
                follow_set |= follow(grammar, start_symbol, production[0])
                return follow_set
    for element in (prod[1] for prod in grammar if symbol in prod[1]):
        for symb in element[element.index(symbol)+1:]:
            if not symb.isupper():
                follow_set.add(symb)
                break
            else:
                first_symb = first(grammar, symb)
                if "epsilon" in first_symb:
                    follow_set |= first_symb.difference({'epsilon'})
                    follow_set |= follow(grammar, start_symbol, symb)
                else:
                    follow_set |= first_symb
    return follow_set

grammar = [
    ('E', 'TA'),
    ('A', '+TA'),
    ('A', 'epsilon'),
    ('T', 'FB'),
    ('B', '*FB'),
    ('B', 'epsilon'),
    ('F', '(E)'),
    ('F', 'd'),
]

non_terminals_set = set(left_side for left_side, _ in grammar)
terminals_set = set()
for nt in non_terminals_set:
    terminals_set |= {c for c in nt if c.islower()}
    terminals_set |= {c for c in nt if c.isnumeric()}
    terminals_set |= {'+', '*', '(', ')','$'}
non_terminals = sorted(list(non_terminals_set))
terminals = sorted(list(terminals_set))

first_sets = {}
follow_sets = {}
for nt in non_terminals:
    first_sets[nt] = first(grammar, nt)
    follow_sets[nt] = follow(grammar, "E", nt)

print("Grammar Rules:")
for rule in grammar:
    print(f"{rule[0]} -> {rule[1]}")    

print("\nFirst Sets:")
for nt in non_terminals:
    print(f"First({nt}) = {first_sets[nt]}")

print("\nFollow Sets:")
for nt in non_terminals:
    print(f"Follow({nt}) = {follow_sets[nt]}")