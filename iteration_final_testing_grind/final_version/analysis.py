import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def aggregate_stats(stats_list):
    """Convert a list of per-frame stats dicts to a dict of lists for plotting/analysis."""
    keys = stats_list[0].keys()
    agg = {k: [] for k in keys}
    for s in stats_list:
        for k in keys:
            agg[k].append(s[k])
    return agg

def plot_population_dynamics(stats):
    frames = stats['frame']
    plt.figure(figsize=(10, 5))
    plt.plot(frames, stats['herbivores'], label='Herbivores', color='blue')
    plt.plot(frames, stats['carnivores'], label='Carnivores', color='red')
    plt.xlabel('Frame')
    plt.ylabel('Population')
    plt.legend()
    plt.title('Population Dynamics')
    plt.tight_layout()
    plt.show()

def plot_trait_evolution(stats, trait):
    frames = stats['frame']
    plt.figure(figsize=(10, 5))
    if f'mean_{trait}_herb' in stats:
        plt.plot(frames, stats[f'mean_{trait}_herb'], label=f'Herbivore {trait}', color='blue')
    if f'mean_{trait}_carni' in stats:
        plt.plot(frames, stats[f'mean_{trait}_carni'], label=f'Carnivore {trait}', color='red')
    plt.xlabel('Frame')
    plt.ylabel(f'Mean {trait}')
    plt.legend()
    plt.title(f'Evolution of {trait}')
    plt.tight_layout()
    plt.show()

def save_stats_to_csv(stats, filename='simulation_stats.csv'):
    df = pd.DataFrame(stats)
    df.to_csv(filename, index=False)
    print(f"Saved statistics to {filename}")

# Example usage after running the simulation:
# stats_list = [grid.get_stats(frame) for frame in range(num_frames)]
# agg_stats = aggregate_stats(stats_list)
# plot_population_dynamics(agg_stats)
# plot_trait_evolution(agg_stats, 'speed')
# save_stats_to_csv(agg_stats)
