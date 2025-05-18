import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Wczytaj dane
df = pd.read_csv("simulation_stats.csv")

# Ustal generacje co 20
generations = sorted(df['generation'].unique())
gen20 = [g for g in generations if g % 20 == 0]

# Kolory dla generacji co 20
colors = plt.cm.get_cmap('tab10', len(gen20))

# WYKRES 1: Populacja Prey
plt.figure(figsize=(12, 6))
for idx, g in enumerate(gen20):
    gen_df = df[df['generation'] == g]
    plt.plot(gen_df['tick'], gen_df['preys_alive'], label=f'Gen {g}', color=colors(idx))
plt.xlabel('Tick')
plt.ylabel('Prey Population')
plt.title('Prey Population per Tick (every 20th generation)')
plt.legend(title="Generation (co 20)", bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
plt.grid(True)
plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.show()

# WYKRES 2: Populacja Predator
plt.figure(figsize=(12, 6))
for idx, g in enumerate(gen20):
    gen_df = df[df['generation'] == g]
    plt.plot(gen_df['tick'], gen_df['predators_alive'], label=f'Gen {g}', color=colors(idx))
plt.xlabel('Tick')
plt.ylabel('Predator Population')
plt.title('Predator Population per Tick (every 20th generation)')
plt.legend(title="Generation (co 20)", bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
plt.grid(True)
plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.show()
