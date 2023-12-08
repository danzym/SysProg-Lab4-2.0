def read_grammar(grammar_str):
    grammar = {}
    # Use strip() to remove extra spaces and empty lines
    lines = grammar_str.strip().splitlines()
    for line in lines:
        if line and ' -> ' in line:  # Check if the line is not empty and contains the separator
            head, body = line.split(' -> ')
            productions = body.split(' | ')
            grammar[head] = productions
        elif line:
            # This block will now only execute for non-empty lines that do not match the format
            print(f"Warning: Line '{line}' does not match the expected format and will be skipped.")
    return grammar


grammar_str = """
S -> AC
A -> a | ε
C -> cb
"""
grammar = read_grammar(grammar_str)


def first_func(symbol, grammar, first_sets):
    """
    Calculates the First set for a symbol.
    """
    # If it's a terminal or epsilon, First is the symbol itself
    if not symbol.isupper() or symbol == 'ε':
        return {symbol}

    # If it's a non-terminal, add the first symbol of each production
    first = set()
    productions = grammar[symbol]
    for prod in productions:
        if prod == 'ε':  # For epsilon productions
            first.add('ε')
        else:
            for char in prod:
                char_first = first_func(char, grammar, first_sets)
                first.update(char_first - {'ε'})
                if 'ε' not in char_first:
                    break
            else:
                first.add('ε')
    return first


def follow_func(symbol, grammar, first_sets, follow_sets):
    """
    Calculates the Follow set for a symbol.
    """
    # For the start symbol, add the end of the input string $
    if symbol == 'S':
        follow_sets[symbol] = set('$')
    else:
        follow_sets[symbol] = set()

    # Review all productions where symbol appears
    for key, productions in grammar.items():
        for prod in productions:
            if symbol in prod:
                symbol_index = prod.index(symbol)
                # If the symbol is not at the end of the production
                if symbol_index + 1 < len(prod):
                    next_symbol = prod[symbol_index + 1]
                    follow_sets[symbol].update(first_sets[next_symbol] - {'ε'})
                # If the symbol is at the end of the production or the next symbol leads to ε
                if symbol_index + 1 == len(prod) or 'ε' in first_sets[prod[symbol_index + 1]]:
                    if key != symbol:  # to avoid recursion
                        follow_sets[symbol].update(follow_sets[key])


# Calculate First and Follow sets for all non-terminals
first_sets = {symbol: first_func(symbol, grammar, {}) for symbol in grammar}
follow_sets = {}
for symbol in grammar:
    follow_func(symbol, grammar, first_sets, follow_sets)

# Display the results
print('First:')
print(first_sets)
print('Follow:')
print(follow_sets)


# Parsing table for LL(1) parser
def create_parsing_table(grammar, first_sets, follow_sets):
    """
    Creates a parsing table for an LL(1) parser.
    """
    parsing_table = {}

    for head, productions in grammar.items():
        for prod in productions:
            if prod != 'ε':
                # Calculate First for each symbol in the production
                first_of_prod = set()
                for char in prod:
                    first_of_char = first_func(char, grammar, first_sets)
                    first_of_prod.update(first_of_char - {'ε'})
                    # If the symbol does not lead to ε, break
                    if 'ε' not in first_of_char:
                        break
                else:
                    # If all symbols in the production lead to ε, add ε to the First set
                    first_of_prod.add('ε')

                for terminal in first_of_prod:
                    parsing_table[(head, terminal)] = prod
            else:
                for terminal in follow_sets[head]:
                    parsing_table[(head, terminal)] = prod

    return parsing_table


# Create the parsing table using defined First and Follow sets
parsing_table = create_parsing_table(grammar, first_sets, follow_sets)

print('Parsimg table:')
print(parsing_table)


def parse_input(input_string, parsing_table, grammar):
    """
    Function for parsing the input string using the LL(1) parser.
    """
    # Stack for parsing
    stack = ['$', 'S']
    # Add the end of the input string
    input_string += '$'

    # Index for the input string
    index = 0

    # Parsing the input string
    while stack[-1] != '$':
        top = stack.pop()
        current_input = input_string[index]

        if top.isupper():
            # Use the parser table for non-terminals
            if (top, current_input) in parsing_table:
                production = parsing_table[(top, current_input)]
                # Add the production to the stack in reverse order
                stack.extend(reversed(production))
            else:
                # Error: no production for this input symbol
                return f"Syntax error: no rule for {top} with input {current_input}"
        else:
            # Input symbol matches the top of the stack
            if top == current_input:
                index += 1  # Read the next symbol
            else:
                # Error: expected symbol does not match the input
                return f"Syntax error: expected {top}, but found {current_input}"

    # Check if the entire input string was read
    if input_string[index] == '$':
        return "Input successfully parsed"
    else:
        return "Syntax error: input not fully parsed"


# Examples for parsing
successful_input = "acb"
error_input = "ab"

# Parse both examples
successful_parse_result = parse_input(successful_input, parsing_table, grammar)
error_parse_result = parse_input(error_input, parsing_table, grammar)

print(f"\nInput {successful_input} -> {successful_parse_result}")
print(f"Input {error_input} -> {error_parse_result}")


class RecursiveDescentParser:
    def __init__(self, input_string):
        self.input = input_string
        self.index = 0
        self.length = len(input_string)

    def look_ahead(self):
        # Returns the next character without consuming it
        return self.input[self.index] if self.index < self.length else '$'

    def consume(self, symbol):
        # Consumes the next symbol if it matches
        if self.look_ahead() == symbol:
            self.index += 1
        else:
            raise ValueError(f"Unexpected symbol {self.input[self.index]}. Expected: {symbol}")

    def parse_S(self):
        # S -> AC
        self.parse_A()
        self.parse_C()

    def parse_A(self):
        # A -> a | ε
        if self.look_ahead() == 'a':
            self.consume('a')
        # If the next symbol is not 'a', assume its epsilon and do nothing

    def parse_C(self):
        # C -> cb
        self.consume('c')
        self.consume('b')

    def parse(self):
        # Begins parsing with the start symbol
        self.parse_S()

        # If we have successfully consumed the entire input string, we are done
        if self.index == self.length:
            return "successfully parsed"
        else:
            raise ValueError("not fully parsed")


# For check
print("\nRecursive:")
test_strings = ["acb", "ab"]

# For analyzer check
for s in test_strings:
    parser = RecursiveDescentParser(s)
    try:
        result = parser.parse()
        print(f"'{s}': {result}")
    except ValueError as e:
        print(f"'{s}': Error - {e}")
