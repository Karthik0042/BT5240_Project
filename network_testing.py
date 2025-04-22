import networkx as nx
import matplotlib.pyplot as plt
import random
import time

# Optional for live plot updating in Jupyter



# Create an empty graph
G = nx.Graph()

# Set of possible nodes
all_nodes = list(range(1, 11))  # Nodes 1 to 10

# Set of possible edges (all combinations)
all_edges = [(i, j) for i in all_nodes for j in all_nodes if i < j]

# Live plot settings
plt.ion()
fig, ax = plt.subplots(figsize=(8, 6))


def draw_graph(G, ax):
    ax.clear()
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color='skyblue', edge_color='gray', ax=ax)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
    ax.set_title("Dynamic Graph Visualization with Edge Weights")
    plt.pause(0.5)


# Run dynamic updates
for _ in range(30):
    # Randomly add or remove a node
    if random.random() < 0.9 and len(G.nodes) < len(all_nodes):
        new_node = random.choice([n for n in all_nodes if n not in G.nodes])
        G.add_node(new_node)
    elif len(G.nodes) > 1:
        rem_node = random.choice(list(G.nodes))
        G.remove_node(rem_node)

    # Randomly add or remove an edge
    possible_edges = [e for e in all_edges if e[0] in G.nodes and e[1] in G.nodes]
    existing_edges = list(G.edges)

    if random.random() < 0.9 and possible_edges:
        new_edge = random.choice([e for e in possible_edges if e not in existing_edges])
        G.add_edge(*new_edge,weight = 10)
    elif existing_edges:
        rem_edge = random.choice(existing_edges)
        G.remove_edge(*rem_edge)

    draw_graph(G, ax)
    time.sleep(0)

plt.ioff()
plt.show()
