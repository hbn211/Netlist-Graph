import argparse

def load_data(file_content):
    if "PROTEL" in file_content:
        # Protel2 format
        components, nets = parse_protel2_netlist(file_content)
    elif "EESchema" in file_content:
        # Kicad format
        components, nets=parse_kicad_netlist(file_content)
    else:
        raise ValueError("Unknown file format.")
    
    return nets, components


def extract_description(file_content, designator):
    # Detect file format
    if "PROTEL" in file_content:
        # Protel2 format
        sections = file_content.split('[')
        for section in sections:
            if designator in section:
                lines = section.split('\n')
                comment, description = None, None
                for i in range(len(lines)):
                    if lines[i].strip() == 'Comment':
                        comment = lines[i + 1].strip()
                    if lines[i].strip() == 'DESCRIPTION':
                        description = lines[i + 1].strip()
                return comment + ' | ' + description
    elif "EESchema" in file_content:
        # Kicad format
        for group in file_content.split('( /'):
            line_group = group.split('\n')
            for index, line in enumerate(line_group):
                if index == 0:
                    if not re.match(r'\s*\(', line):
                        if designator == line.split(' ')[-2]:
                            return line.split(' ')[-1]
    return None


def parse_protel2_netlist(file_content):
    nets = {}
    current_net = None
    inside_net = False
    lines = file_content.split('\n')

    for line in lines:
        line = line.strip()
        if line.startswith('[') or line.endswith(']'):
            continue
        elif line == '(':
            inside_net = True
            continue
        elif inside_net and current_net is None:
            current_net = line
            nets[current_net] = []
        elif line == ')':
            inside_net = False
            current_net = None
        elif inside_net:
            pin_info = line.split()
            if len(pin_info) < 1:
                continue
            designator_pin = pin_info[0]
            nets[current_net].append(designator_pin)

    component_pins = {}

    for net, connections in nets.items():
        for connection in connections:
            component, pin = connection.split('-')
            if component not in component_pins:
                component_pins[component] = []
            component_pins[component].append(connection)

    return component_pins, nets

def create_component_pin_list_protel(nets):
    component_pins = {}

    for net, connections in nets.items():
        for connection in connections:
            component, pin = connection.split('-')
            if component not in component_pins:
                component_pins[component] = []
            component_pins[component].append(connection)
    return component_pins

import re
def parse_kicad_netlist(file_content):
    component_pins = {}
    nets = {}

    for group in file_content.split('( /'):
        line_group = group.split('\n')
        designator = None

        for index, line in enumerate(line_group):
            if index == 0:
                if not re.match(r'\s*\(', line):
                    designator = line.split(' ')[-2]
                    if designator not in component_pins:
                        component_pins[designator] = []
            else:
                if re.match(r'\s*\(', line) and line.endswith(' )'):
                    newline = line.split(' ')
                    pin = newline[-3]
                    net = newline[-2]
                    pin_designator = f"{designator}-{pin}"
                    
                    component_pins[designator].append(pin_designator)
                    
                    if net not in nets:
                        nets[net] = []
                    nets[net].append(pin_designator)

    return component_pins, nets


def main():
    # Setup argparse
    parser = argparse.ArgumentParser(description="Test functions from the loader script")
    
    # Add subcommands for each function
    subparsers = parser.add_subparsers(dest="function", help="Available functions")
    
    # Subcommand for extract_description
    parser_extract = subparsers.add_parser("extract_description", help="Extract description of a designator")
    parser_extract.add_argument("file_path", type=str, help="Path to the file")
    parser_extract.add_argument("designator", type=str, help="Component designator (e.g., R10, J15)")
    
    # Subcommand for parse_protel2_netlist
    parser_protel2 = subparsers.add_parser("parse_protel2_netlist", help="Parse Protel2 netlist")
    parser_protel2.add_argument("file_path", type=str, help="Path to the file")
            
    # Subcommand for parse_kicad_netlist
    parser_protel2 = subparsers.add_parser("parse_kicad_netlist", help="Parse Protel2 netlist")
    parser_protel2.add_argument("file_path", type=str, help="Path to the file")

    # Parse arguments
    args = parser.parse_args()

    # Read file content
    try:
        with open(args.file_path, 'r', encoding='latin-1') as file:
            file_content = file.read()
    except FileNotFoundError:
        print(f"File not found: {args.file_path}")
        return

    # Call appropriate function based on argument
    if args.function == "extract_description":
        description = extract_description(file_content, args.designator)
        if description:
            print(f"Designator: {args.designator} - Description: {description}")
        else:
            print(f"No description found for designator {args.designator}")
    
    elif args.function == "parse_protel2_netlist":
        components,nets = parse_protel2_netlist(file_content)
        print("Component Pin List:", components)
        print(" ")
        print("Parsed kicad Nets:", nets)
    

    elif args.function == "parse_kicad_netlist":
        components,nets = parse_kicad_netlist(file_content)
        print("Component Pin List:", components)
        print(" ")
        print("Parsed kicad Nets:", nets)

    else:
        print("No valid function specified. Use -h or --help for more information.")

if __name__ == "__main__":
    main()