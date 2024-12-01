import re

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.current_address = 0
        self.counter = 0

    def add_symbol(self, name, data_type, size, line_number, value=None, dimensions=0):
        if name not in self.symbols:
            symbol_entry = {
                "Counter": self.counter,
                "Variable Name": name,
                "Address": self.current_address,
                "Data Type": data_type,
                "Size (bytes)": size,
                "No. of Dimensions": dimensions,
                "Line Declaration": line_number,
                "References": set(),
                "Value": value
            }
            self.symbols[name] = symbol_entry
            self.counter += 1
            self.current_address += size
        self.add_reference(name, line_number)

    def add_reference(self, name, line_number):
        if name in self.symbols:
            if line_number != self.symbols[name]["Line Declaration"]:
                self.symbols[name]["References"].add(line_number)

def calculate_string_size(value):
    if value.startswith('"') and value.endswith('"'):
        return len(value[1:-1])
    return len(value)

def calculate_array_size(data_type, elements):
    base_sizes = {'int': 2, 'float': 4, 'char': 1}
    if not elements:
        return base_sizes.get(data_type, 4)
    
    elements = elements.strip('[]').split(',')
    if data_type == 'string':
        total_size = 0
        for elem in elements:
            elem = elem.strip()
            if elem.startswith('"') and elem.endswith('"'):
                total_size += len(elem[1:-1])
        return total_size
    return base_sizes.get(data_type, 4) * len(elements)

def infer_list_type(elements):
    elements = elements.strip('[]').split(',')
    first_elem = elements[0].strip()
    if first_elem.startswith('"'):
        return 'string'
    try:
        float(first_elem)
        if '.' in first_elem:
            return 'float'
        return 'int'
    except ValueError:
        return 'unknown'

def generate_symbol_table(source_code):
    symbol_table = SymbolTable()
    data_type_sizes = {'int': 2, 'float': 4, 'char': 1, 'unknown': 0}
    lines = source_code.splitlines()
    for line_number, line in enumerate(lines, 1):
        for_loop_match = re.search(r'for\s+(\w+)\s+in\s+(\[[^]]+\])', line)
        if for_loop_match:
            iterator_name = for_loop_match.group(1)
            target_list = for_loop_match.group(2)
            list_type = infer_list_type(target_list)
            
            if list_type == 'string':
                elements = re.findall(r'"([^"]*)"', target_list)
                size = max(len(s) for s in elements) if elements else 1
            else:
                size = data_type_sizes.get(list_type, 4)
            
            symbol_table.add_symbol(iterator_name, list_type, size, line_number)
            continue

        declarations = re.findall(r'\b(int|float|char|string)\s+(\w+)(?:\s*=\s*([^;]+))?', line)
        for data_type, var_name, value in declarations:
            if value and value.strip().startswith('['):
                size = calculate_array_size(data_type, value.strip())
                symbol_table.add_symbol(var_name, f"{data_type}[]", size, line_number, value.strip(), 1)
            else:
                if data_type == 'string' and value:
                    size = calculate_string_size(value.strip())
                else:
                    size = data_type_sizes.get(data_type, 4)
                symbol_table.add_symbol(var_name, data_type, size, line_number, value.strip() if value else None)
        line_without_strings = re.sub(r'"[^"]*"', '', line)

        variables_in_line = re.findall(r'\b([a-zA-Z_]\w*)\b', line_without_strings)
        keywords = {'if', 'print', 'in', 'else', 'for', 'while', 'return', 'int', 'float',
            'range', 'string', 'elif', 'pass', 'break', 'continue', 'True', 
            'False', 'and', 'or', 'not', 'begin', 'end'}
        for var in variables_in_line:
            if var in symbol_table.symbols:
                symbol_table.add_reference(var, line_number)
            elif var not in keywords and not var.startswith('"'):
                symbol_table.add_symbol(var, 'unknown', data_type_sizes['unknown'], line_number)

    return symbol_table

def print_symbol_table(symbol_table):
    print("\nSymbol Table:\n")
    print(f"{'Counter':<8}{'Variable Name':<15}{'Address':<10}{'Data Type':<15}{'Size (bytes)':<15}"
          f"{'No. of Dimensions':<20}{'Line Declaration':<20}{'References':<20}{'Value'}")
    print("-" * 120)
    
    for name, entry in symbol_table.symbols.items():
        print(f"{entry['Counter']:<8}"
              f"{entry['Variable Name']:<15}"
              f"{entry['Address']:<10}"
              f"{entry['Data Type']:<15}"
              f"{entry['Size (bytes)']:<15}"
              f"{entry['No. of Dimensions']:<20}"
              f"{entry['Line Declaration']:<20}"
              f"{str(entry['References']):<20}"
              f"{entry['Value'] if entry['Value'] is not None else 'None'}")

#================================================================

def read_source_code(file_path):
    with open(file_path, 'r') as file:
        return file.read()

source_file_path = 'source_code.txt' 
source_code = read_source_code(source_file_path)
def main():
    symbol_table = generate_symbol_table(source_code)
    print_symbol_table(symbol_table)

if __name__ == "__main__":
    main()