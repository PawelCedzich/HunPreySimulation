import pandas as pd
import matplotlib.pyplot as plt

# Wczytaj dane
df = pd.read_csv("simulation_stats3.csv")

# Dodaj kolumnę z numerem batcha (co 10 generacji)
df['batch10'] = df['generation'] // 10

# Grupuj po batchu i ticku, obliczając średnią populację dla batcha (czyli 10 generacji razem)
batch_prey = df.groupby(['batch10', 'tick'])['preys_alive'].mean().reset_index()
batch_pred = df.groupby(['batch10', 'tick'])['predators_alive'].mean().reset_index()

# WYKRES 1: Średnia populacja Zwierzyny (dla batcha 10 generacji)
plt.figure(figsize=(12, 6))
for batch in sorted(batch_prey['batch10'].unique()):
    batch_df = batch_prey[batch_prey['batch10'] == batch]
    plt.plot(batch_df['tick'], batch_df['preys_alive'], label=f'{int(batch)*10}-{int(batch)*10+9}')
plt.xlabel('Tick')
plt.ylabel('Średnia populacji zwierzyny (co 10 generacji)')
plt.title('Średnia populacja zwierzyny na Tick (co 10 generacji)')
plt.legend(title="Generacje:", bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
plt.grid(True)
plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.show()

# WYKRES 2: Średnia populacja Drapieżnika (dla batcha 10 generacji)
plt.figure(figsize=(12, 6))
for batch in sorted(batch_pred['batch10'].unique()):
    batch_df = batch_pred[batch_pred['batch10'] == batch]
    plt.plot(batch_df['tick'], batch_df['predators_alive'], label=f'{int(batch)*10}-{int(batch)*10+9}')
plt.xlabel('Tick')
plt.ylabel('Średnia populacji drapieżnika (co 10 generacji)')
plt.title('Średnia populacja drapieżnika na Tick (co 10 generacji)')
plt.legend(title="Generacje:", bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
plt.grid(True)
plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.show()
