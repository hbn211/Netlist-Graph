import networkx as nx
from pyvis.network import Network
from collections import deque

import loader

def create_graph(nets, components, blacklist_nets, blacklist_components):
    G = nx.Graph()
    
    for net, nodes in nets.items():
        if net in blacklist_nets:
            continue
        for node in nodes:
            G.add_edge(node, net)
    
    for component, nodes in components.items():
        if component in blacklist_components:
            continue
        for node in nodes:
            G.add_edge(node, component)
    
    return G


def find_path_bfs(graph, initial_node, component_target, num_path=1, nets=None):
    is_target_node = '-' in component_target
    
    queue = deque([(initial_node, [initial_node])])
    visited = set([initial_node])

    paths = []
    while queue and len(paths) < num_path:
        current_node, path_s = queue.popleft()

        for neighbor in graph.neighbors(current_node):
            if neighbor == component_target:
                if not is_target_node or (is_target_node and current_node in nets):
                    paths.append(path_s + [neighbor])
                    print(f"Path found: {' -> '.join(path_s + [neighbor])}")
                    if len(paths) >= num_path:
                        return paths
                continue
            
            if neighbor not in visited and not neighbor.startswith('Comp') and not neighbor.startswith(initial_node.split('-')[0]):
                queue.append((neighbor, path_s + [neighbor]))
                visited.add(neighbor)

    return paths if paths else None


def find_nodes_up_to_depth(graph, initial_node, max_depth):
    queue = deque([(initial_node, 0)])
    visited = set([initial_node])
    nodes_found = {initial_node}

    while queue:
        current_node, depth = queue.popleft()
        if depth < max_depth:
            for neighbor in graph.neighbors(current_node):
                if neighbor not in visited and not neighbor.startswith('Comp') and not neighbor.startswith(initial_node.split('-')[0]):
                    visited.add(neighbor)
                    nodes_found.add(neighbor)
                    queue.append((neighbor, depth + 1))
    
    return nodes_found


def generate_html_parameters(initial_node, component_target, max_depth, blacklist_nets, blacklist_components, num_path):
    parameters_html = f"""
    <style>
        .parameters-container {{
            position: absolute;
            top: 10px;
            left: 10px;
            background-color: rgba(255, 255, 255, 0.8);
            border: 1px solid #ccc;
            padding: 10px;
            z-index: 1000;
        }}
    </style>
    <div class="parameters-container">
        <h2>Configuration Parameters</h2>
        <ul>
            <li><strong>Initial Node:</strong> {initial_node}</li>
            <li><strong>Target Component:</strong> {component_target}</li>
            <li><strong>Maximum Depth:</strong> {max_depth}</li>
            <li><strong>Number of Paths:</strong> {num_path}</li>
            <li><strong>Nets in the Blacklist:</strong> {', '.join(blacklist_nets)}</li>
            <li><strong>Components in the Blacklist:</strong> {', '.join(blacklist_components)}</li>
        </ul>
    </div>
    """
    return parameters_html


def graphs(file_content, nets, components, initial_node, component_target=None, max_depth=None, blacklist_nets=None, blacklist_components=None,num_path=1):
    if blacklist_components is None: blacklist_components = ''
    if blacklist_nets is None: blacklist_nets = ''
    if max_depth is None: max_depth = 0
    elif max_depth < 0: max_depth = 0
    
    graph = create_graph(nets, components, blacklist_nets, blacklist_components)

    if component_target is not None:
        path_s = find_path_bfs(graph, initial_node, component_target,num_path=num_path,nets=nets)
        if path_s:
            for i, path in enumerate(path_s, 1):
                print(f"Path {i} found: {' -> '.join(path)}")
        else:
            print("No path found.")
            component_target = None
            path_s = []
    else: path_s = []

    nodes_found = find_nodes_up_to_depth(graph, initial_node, max_depth)
    print(f"Nodes found up to depth {max_depth}: {', '.join(nodes_found)}")

    subgraph_nodes = set(nodes_found).union(set(node for path in path_s for node in path))
    subgraph_edges = [(u, v) for u, v in graph.edges() if u in subgraph_nodes and v in subgraph_nodes]

    subgraph = graph.subgraph(subgraph_nodes)

    net = Network(notebook=True, cdn_resources='in_line', width="100%", height="100vh")

    for node in subgraph.nodes():
        title_info = None
        
        if node in nets: shapeif='text'
        elif node in components: 
            shapeif='square'
            title_info=loader.extract_description(file_content, node)
        else: shapeif='box'
        
        if (node == initial_node): 
            colorif='lime'
            labelif='Source '+initial_node
        elif (node == component_target): 
            colorif='red'
            labelif='Target '+component_target
        else: 
            colorif=None
            labelif=None
        
        if title_info is None: net.add_node(node, label=labelif, color=colorif,shape=shapeif)
        else: net.add_node(node, label=labelif, color=colorif,shape=shapeif,title=title_info)

    for edge in subgraph.edges():
        if edge[0] in nets or edge[1] in nets:
            net.add_edge(edge[0], edge[1], color='red', width=1)
        else:
            net.add_edge(edge[0], edge[1], color='blue', width=5)

    html_content = net.generate_html()

    css_styles = """
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
    </style>
    """
    html_content = html_content.replace('<head>', '<head>' + css_styles)

    parameters_html = generate_html_parameters(initial_node, component_target, max_depth, blacklist_nets, blacklist_components,num_path)
    html_content = html_content.replace('</body>', parameters_html + '</body>')
    
    with open("graph.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    import webbrowser
    webbrowser.open("graph.html")