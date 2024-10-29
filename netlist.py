import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import loader
import graph

def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Netlist Files", "*.NET")])
    if not file_path:
        return None, None, None
    with open(file_path, "r") as file:
        file_content = file.read()
    nets,components=loader.load_data(file_content)
    return file_content, nets, components

def list_components(components):
    return list(components.keys())

def list_pins(components, component):
    if component in components:
        return [pin.split('-')[1] for pin in components[component]]
    return []

def validate_component_pin(components, component_pin):
    return component_pin in list_components(components)

def apply_filter(lista, filter):
    filter = filter.strip()
    if filter.startswith('*'):
        filter = filter[1:]
    if filter.endswith('*'):
        filter = filter[:-1]
    if '*' in filter:
        return lista 
    return [item for item in lista if filter in item]

def refresh_blacklist(filter, original_list, frame, vars_dict):
    estado_atual = {item: var.get() for item, var in vars_dict.items()}

    for widget in frame.winfo_children():
        widget.destroy()

    lista_filtrada = apply_filter(original_list, filter.get())
    
    for item in lista_filtrada:
        var = tk.BooleanVar(value=estado_atual.get(item, False))
        chk = tk.Checkbutton(frame, text=item, variable=var)
        chk.pack(anchor='w')
        vars_dict[item] = var

def clean_blacklists(frame_nets, frame_components, vars_nets, vars_components):
    for widget in frame_nets.winfo_children():
        widget.destroy()
    for widget in frame_components.winfo_children():
        widget.destroy()

    vars_nets.clear()
    vars_components.clear()

def string_length_to_pixels(string_length, font):
    root = tk.Tk()
    canvas = tk.Canvas(root)
    text_id = canvas.create_text(0, 0, text="A" * string_length, font=font, anchor="nw")
    bbox = canvas.bbox(text_id)
    root.destroy()
    return bbox[2] - bbox[0]
    
def select_component(event, component_var, components_with_description, update_pins):
    typed_component = component_var.get().split(' ')
    for item in components_with_description:
        if item.startswith(typed_component[0]):
            component_var.set(item)
            update_pins()
            break

def select_component_NOPIN(event, component_var, components_with_description):
    typed_component = component_var.get().split(' ')
    for item in components_with_description:
        if item.startswith(typed_component[0]):
            component_var.set(item)
            break

def split_letters_numbers(text):
    partes = re.findall(r'\D+|\d+', text)
    return [int(parte) if parte.isdigit() else parte for parte in partes]

def sort_letters_numbers(lista):
    return sorted(lista, key=split_letters_numbers)

def start_interface():
    def load_file_callback(file_content_var):
        global components, nets, file_content, components_list, sorted_nets, components_with_description
        file_content, nets, components = load_file()
        if file_content is None:
            messagebox.showerror("Error", "No file loaded.")
            return
        file_content_var.set("File loaded!")
        component_var.set('')
        
        clean_blacklists(scrollable_frame_nets, scrollable_frame_components, blacklist_nets_vars, blacklist_components_vars)
        
        components_list = list_components(components)
        components_list = sort_letters_numbers(components_list)
        components_with_description = [f"{comp} ({loader.extract_description(file_content, comp)})" for comp in components_list]
        max_length = max(len(comp) for comp in components_with_description)
        components_dropdown.config(width=max_length)
        components_dropdown['values'] = components_with_description

        components_target_dropdown.config(width=max_length)
        components_target_dropdown['values'] = components_with_description

        def update_pins(*args):
            components_selecionado = component_var.get().split(' ')
            pins_list = list_pins(components, components_selecionado[0])
            pins_list = sort_letters_numbers(pins_list)
            pin_dropdown['values'] = pins_list
            pin_var.set('')

        component_var.trace_add("write", update_pins)
        components_dropdown.bind("<Return>", lambda event: select_component(event, component_var, components_with_description, update_pins))

        components_target_dropdown.bind("<Return>", lambda event: select_component_NOPIN(event, components_target_var, components_with_description))

        sorted_nets = sorted(nets.keys(), key=lambda net: len(nets[net]), reverse=True)

        refresh_blacklist(filter_nets_var, sorted_nets, scrollable_frame_nets, blacklist_nets_vars)
        refresh_blacklist(filter_components_var, components_list, scrollable_frame_components, blacklist_components_vars)

    root = tk.Tk()
    root.title("Netlist configuration")
    file_frame = tk.Frame(root)
    file_frame.pack(pady=5)

    tk.Label(file_frame, text="Select the netlist file:").grid(row=0, column=0)
    file_content_var = tk.StringVar()
    tk.Button(file_frame, text="Load file", command=lambda: load_file_callback(file_content_var)).grid(row=0, column=1, padx=5)
    tk.Label(file_frame, textvariable=file_content_var).grid(row=0, column=2, padx=5)

    filter_components_var = tk.StringVar()

    tk.Label(root, text="Select initial component:").pack(pady=5)
    component_var = tk.StringVar()
    components_dropdown = ttk.Combobox(root, textvariable=component_var)
    components_dropdown.pack(pady=5)

    tk.Label(root, text="Select initial pin:").pack(pady=5)
    pin_var = tk.StringVar()
    pin_dropdown = ttk.Combobox(root, textvariable=pin_var)
    pin_dropdown.pack(pady=5)

    tk.Label(root, text="Component Target:").pack(pady=5)
    components_target_var = tk.StringVar()
    components_target_dropdown = ttk.Combobox(root, textvariable=components_target_var)
    components_target_dropdown.pack(pady=5)

    tk.Label(root, text="Select target pin:").pack(pady=5)
    pin_target_var = tk.StringVar()
    pin_target_dropdown = ttk.Combobox(root, textvariable=pin_target_var)
    pin_target_dropdown.pack(pady=5)

    def update_target_pins(*args):
        component_target = components_target_var.get().split(' ')[0]
        pins_target_list = list_pins(components, component_target)
        pins_target_list = sort_letters_numbers(pins_target_list)
        pin_target_dropdown['values'] = pins_target_list
        pin_target_var.set('')

    components_target_var.trace_add("write", update_target_pins)
    components_target_dropdown.bind("<Return>", lambda event: select_component_NOPIN(event, components_target_var, components_with_description))

    depth_num_path_frame = tk.Frame(root)
    depth_num_path_frame.pack(pady=5)

    tk.Label(depth_num_path_frame, text="Maximum depth:").grid(row=0, column=0, padx=(0, 5))
    depth_max_var = tk.StringVar(value='0')
    depth_max_entry = tk.Entry(depth_num_path_frame, textvariable=depth_max_var, width=10)
    depth_max_entry.grid(row=0, column=1)

    tk.Label(depth_num_path_frame, text="Path number:").grid(row=0, column=2, padx=(10, 5))
    num_path_var = tk.StringVar(value='1')
    num_path_entry = tk.Entry(depth_num_path_frame, textvariable=num_path_var, width=10)
    num_path_entry.grid(row=0, column=3)

    blacklist_frame = tk.Frame(root)
    blacklist_frame.pack(pady=5, fill=tk.BOTH, expand=True)

    tk.Label(blacklist_frame, text="Net filter:").grid(row=0, column=0)
    filter_nets_var = tk.StringVar()
    filter_nets_entry = tk.Entry(blacklist_frame, textvariable=filter_nets_var)
    filter_nets_entry.grid(row=1, column=0)

    tk.Label(blacklist_frame, text="Components filter:").grid(row=0, column=1)
    filter_components_blacklist_var = tk.StringVar()
    filter_components_blacklist_entry = tk.Entry(blacklist_frame, textvariable=filter_components_blacklist_var)
    filter_components_blacklist_entry.grid(row=1, column=1)

    nets_frame = tk.Frame(blacklist_frame)
    nets_frame.grid(row=2, column=0, sticky='nsew')
    canvas_nets = tk.Canvas(nets_frame)
    scrollbar_nets = tk.Scrollbar(nets_frame, orient="vertical", command=canvas_nets.yview)
    scrollable_frame_nets = tk.Frame(canvas_nets)
    scrollable_frame_nets.bind("<Configure>", lambda e: canvas_nets.configure(scrollregion=canvas_nets.bbox("all")))
    canvas_nets.create_window((0, 0), window=scrollable_frame_nets, anchor="nw")
    canvas_nets.configure(yscrollcommand=scrollbar_nets.set)
    scrollbar_nets.pack(side="right", fill="y")
    canvas_nets.pack(side="left", fill="both", expand=True)

    components_frame = tk.Frame(blacklist_frame)
    components_frame.grid(row=2, column=1, sticky='nsew')
    canvas_components = tk.Canvas(components_frame)
    scrollbar_components = tk.Scrollbar(components_frame, orient="vertical", command=canvas_components.yview)
    scrollable_frame_components = tk.Frame(canvas_components)
    scrollable_frame_components.bind("<Configure>", lambda e: canvas_components.configure(scrollregion=canvas_components.bbox("all")))
    canvas_components.create_window((0, 0), window=scrollable_frame_components, anchor="nw")
    canvas_components.configure(yscrollcommand=scrollbar_components.set)
    scrollbar_components.pack(side="right", fill="y")
    canvas_components.pack(side="left", fill="both", expand=True)

    blacklist_nets_vars = {}
    blacklist_components_vars = {}

    filter_nets_var.trace_add("write", lambda *args: refresh_blacklist(filter_nets_var, sorted_nets, scrollable_frame_nets, blacklist_nets_vars))
    filter_components_blacklist_var.trace_add("write", lambda *args: refresh_blacklist(filter_components_blacklist_var, components_list, scrollable_frame_components, blacklist_components_vars))

    def execute_graphs():
        initial_node_component = component_var.get().split(' ')[0]
        initial_node_pin = pin_var.get()

        if initial_node_pin:
            initial_node = f"{initial_node_component}-{initial_node_pin}"
        else:
            initial_node = initial_node_component

        component_target_component = components_target_var.get().split(' ')[0]
        component_target_pin = pin_target_var.get()
        
        if component_target_pin:
            component_target = f"{component_target_component}-{component_target_pin}"
        else:
            component_target = component_target_component

        print(f"Initial: {initial_node} Target: {component_target}")
        
        try:
            depth_max = int(depth_max_var.get())
            num_path = int(num_path_var.get())
        except ValueError:
            messagebox.showerror("Error", "Maximun depth and Path number must be integer.")
            return

        blacklist_nets = [net for net, var in blacklist_nets_vars.items() if var.get()]
        blacklist_components = [comp for comp, var in blacklist_components_vars.items() if var.get()]
        graph.graphs(file_content, nets, components, initial_node, component_target, depth_max, blacklist_nets, blacklist_components, num_path=num_path)

    tk.Button(root, text="Execute", command=execute_graphs).pack(pady=20)

    root.mainloop()

start_interface()