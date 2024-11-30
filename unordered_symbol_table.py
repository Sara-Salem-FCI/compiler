
import re

def read_source_code(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Main execution

source_file_path = 'source_code.txt'  # Specify the path to your file
source_code = read_source_code(source_file_path)

# Symbol table generator
def generate_symbol_table(code):
    symbol_table = []
    line_number = 1
    current_address = 0
    counter = 0

    # Data type sizes (in bytes)
    data_type_sizes = {
        'char': 1,
        'int': 2,
        'float': 4,
        'string': 0  # We'll calculate the string size dynamically
    }

    # Regular expressions
    array_declaration_pattern = re.compile(r"^\s*(?P<data_type>int|float|char|string)\s+(?P<variable_name>\w+)\[(?P<size>\d+)\]\s*=\s*\{.*?\};")
    regular_declaration_pattern = re.compile(r"^\s*(?P<data_type>int|float|char|string)\s+(?P<variable_name>\w+)\s*=\s*(?P<value>.*?);")
    simple_declaration_pattern = re.compile(r"^\s*(?P<data_type>int|float|char|string)\s+(?P<variable_name>\w+)\s*;")
    loop_variable_pattern = re.compile(r"for\s*\(\s*(?P<data_type>int|float|char|string)\s+(?P<variable_name>\w+)\s*=")  # Updated to match the loop variable

    for line in code.splitlines():
        # Check for array declarations
        match = array_declaration_pattern.match(line)
        if match:
            data_type = match.group("data_type")
            variable_name = match.group("variable_name")
            size = int(match.group("size"))
            total_size = size * data_type_sizes[data_type]

            symbol_table.append({
                "Counter": counter,
                "Variable Name": variable_name,
                "Address": current_address,
                "Data Type": f"{data_type}[]",
                "Size": total_size,
                "No. of Dimensions": 1,
                "Line Declaration": line_number,
                "Reference Line": set(),
            })
            counter += 1
            current_address += total_size

        # Check for regular declarations with initialization
        match = regular_declaration_pattern.match(line)
        if match:
            data_type = match.group("data_type")
            variable_name = match.group("variable_name")
            value = match.group("value").strip()

            # Handle string type
            if data_type == 'string':
                size = len(value.strip('"'))  # Calculate string length
            else:
                size = data_type_sizes[data_type]

            symbol_table.append({
                "Counter": counter,
                "Variable Name": variable_name,
                "Address": current_address,
                "Data Type": data_type,
                "Size": size,
                "No. of Dimensions": 0,
                "Line Declaration": line_number,
                "Reference Line": set(),
            })
            counter += 1
            current_address += size


# Check for simple declarations without initialization
        match = simple_declaration_pattern.match(line)
        if match:
            data_type = match.group("data_type")
            variable_name = match.group("variable_name")
            size = data_type_sizes[data_type]
            symbol_table.append({
                "Counter": counter,
                "Variable Name": variable_name,
                "Address": current_address,
                "Data Type": data_type,
                "Size": size,
                "No. of Dimensions": 0,
                "Line Declaration": line_number,
                "Reference Line": set(),
            })
            counter += 1
            current_address += size

        # Check for loop variables (now explicitly capturing the loop variable in the 'for' loop)
        match = loop_variable_pattern.search(line)
        if match:
            data_type = match.group("data_type")
            variable_name = match.group("variable_name")
            size = data_type_sizes[data_type]

            # Add loop variable to symbol table
            symbol_table.append({
                "Counter": counter,
                "Variable Name": variable_name,
                "Address": current_address,
                "Data Type": data_type,
                "Size": size,
                "No. of Dimensions": 0,
                "Line Declaration": line_number,
                "Reference Line": set(),
            })
            counter += 1
            current_address += size

        # Update references for variables in the current line
        variables_in_line = re.findall(r"\b\w+\b", line)
        for variable in variables_in_line:
            for entry in symbol_table:
                if entry["Variable Name"] == variable:
                    if line_number != entry["Line Declaration"]:
                        entry["Reference Line"].add(line_number)

        line_number += 1

    return symbol_table

# Generate symbol table from the sample code
symbol_table = generate_symbol_table(source_code)

# Print the symbol table
print("\nSymbol Table:\n")
print(f"{'Counter':<8}{'Variable Name':<15}{'Address':<10}{'Data Type':<15}{'Size (bytes)':<15}{'No. of Dimensions':<20}{'Line Declaration':<20}{'Reference Line'}")
for entry in symbol_table:
    print(f"{entry['Counter']:<8}{entry['Variable Name']:<15}{entry['Address']:<10}{entry['Data Type']:<15}{entry['Size']:<15}{entry['No. of Dimensions']:<20}{entry['Line Declaration']:<20}{str(entry['Reference Line']).replace('set()', '{}')}")