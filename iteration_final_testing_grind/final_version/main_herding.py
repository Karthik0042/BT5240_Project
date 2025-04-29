import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx
from grid import Grid
from organism import Organism

def euclidean(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def find_herbivore_clusters(positions, threshold=3):
    G = nx.Graph()
    for i, pos in enumerate(positions):
        G.add_node(i, pos=pos)
    for i in range(len(positions)):
        for j in range(i+1, len(positions)):
            if euclidean(positions[i], positions[j]) <= threshold:
                G.add_edge(i, j)
    clusters = [list(comp) for comp in nx.connected_components(G)]
    return clusters

# --- Simulation setup ---
grid_size = 50
num_herbivores = 5
num_carnivores = 0
num_food = 120
total_frames = 2000

organisms = [
    Organism(np.random.randint(0, grid_size), np.random.randint(0, grid_size), grid_size, cannibalism=False)
    for _ in range(num_herbivores)
]
organisms += [
    Organism(np.random.randint(0, grid_size), np.random.randint(0, grid_size), grid_size, cannibalism=True)
    for _ in range(num_carnivores)
]

g = Grid(grid_size, num_organisms=num_herbivores + num_carnivores, num_food=num_food)
g.add_organisms(organisms)

fig, (ax_grid, ax_herd) = plt.subplots(1, 2, figsize=(14, 6))

# --- Lattice subplot (left) ---
ax_grid.set_title("Grid Simulation: Herbivores (Blue), Carnivores (Red)")
ax_grid.set_xticks([])
ax_grid.set_yticks([])
ax_grid.set_xlim(0, grid_size)
ax_grid.set_ylim(0, grid_size)
herbivore_scatter = ax_grid.scatter([], [], c='blue', s=20, marker='o', label="Herbivores")
carnivore_scatter = ax_grid.scatter([], [], c='red', s=30, marker='s', label="Carnivores")
food_scatter = ax_grid.scatter([], [], c='green', s=30, marker='x', label="Food")
ax_grid.legend(loc="upper right")

# --- Herding/Clustering subplot (right) ---
ax_herd.set_title("Herbivore Herds (Pink Bubbles)")
ax_herd.set_xticks([])
ax_herd.set_yticks([])
ax_herd.set_xlim(0, grid_size)
ax_herd.set_ylim(0, grid_size)

bubble_artists = []
text_artists = []

def update(frame):
    # Update grid (lattice)
    g.update(frame, herbivore_scatter, carnivore_scatter, food_scatter)

    # Remove old bubbles and texts
    global bubble_artists, text_artists
    for art in bubble_artists:
        art.remove()
    for txt in text_artists:
        txt.remove()
    bubble_artists = []
    text_artists = []

    herbivores = [o for o in g.organisms if not o.cannibalism]
    herb_positions = [(o.x, o.y) for o in herbivores]
    clusters = find_herbivore_clusters(herb_positions, threshold=3)

    # Draw strong pink bubbles with number of herbivores inside
    for cluster in clusters:
        if len(cluster) > 1:
            points = np.array([herb_positions[i] for i in cluster])
            centroid = points.mean(axis=0)
            # Bubble size: scale with number of herbivores
            radius = 0.8 + 0.25 * len(cluster)
            bubble = plt.Circle(centroid, radius=radius, color='#ff1493', alpha=0.6, zorder=1)  # strong pink
            ax_herd.add_patch(bubble)
            bubble_artists.append(bubble)
            # Add number of herbivores at centroid
            txt = ax_herd.text(centroid[0], centroid[1], str(len(cluster)),
                               color='white', fontsize=12, ha='center', va='center', weight='bold', zorder=2)
            text_artists.append(txt)

    # No blue dots: do not plot individual herbivores
    return [herbivore_scatter, carnivore_scatter, food_scatter] + bubble_artists + text_artists

ani = animation.FuncAnimation(
    fig, update, frames=total_frames, blit=False, interval=100, repeat=False
)

plt.tight_layout()
plt.show()
