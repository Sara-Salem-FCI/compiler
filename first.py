def first(grammar, symbol):
    first_set = set()
    
    # If symbol is a terminal, return it
    if not symbol[0].isupper():
        return {symbol}
    
    # Find all productions for this non-terminal
    productions = [prod[1] for prod in grammar if prod[0] == symbol]
    
    for prod in productions:
        # If production is epsilon
        if prod == 'epsilon':
            first_set.add('epsilon')
            continue
        
        # Iterate through symbols in the production
        for char in prod:
            # Get FIRST set of current symbol
            current_first = first(grammar, char)
            
            # Add non-epsilon terminals/non-terminals
            first_set.update(current_first - {'epsilon'})
            
            # If current symbol doesn't derive epsilon, stop
            if 'epsilon' not in current_first:
                break
        else:
            # If all symbols can derive epsilon, add epsilon
            first_set.add('epsilon')
    
    return first_set

# Rest of the code remains the same

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
    terminals_set |= first(grammar, nt).difference({'epsilon'})
non_terminals = list(non_terminals_set)
terminals = list(terminals_set)

print("First Sets:")
for nt in non_terminals:
    print(f'First({nt}) = {first(grammar, nt)}')