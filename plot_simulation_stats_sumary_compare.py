import pandas as pd
import matplotlib.pyplot as plt

# Wczytaj dane z trzech plików
df1 = pd.read_csv("simulation_stats.csv")
df2 = pd.read_csv("simulation_stats2.csv")
df3 = pd.read_csv("simulation_stats3.csv")

# Filtruj tylko ticki co 50 (tak jak logowanie)
df1_tick = df1[df1['tick'] % 50 == 0]
df2_tick = df2[df2['tick'] % 50 == 0]
df3_tick = df3[df3['tick'] % 50 == 0]

# Grupowanie po ticku: sumujemy liczebności dla każdego kroku (ticka) w generacji
prey_sum1 = df1_tick.groupby('tick')['preys_alive'].sum()
prey_sum2 = df2_tick.groupby('tick')['preys_alive'].sum()
prey_sum3 = df3_tick.groupby('tick')['preys_alive'].sum()

# Oś X: ticki co 50 (wspólna dla wszystkich plików)
ticks = sorted(set(prey_sum1.index).union(prey_sum2.index).union(prey_sum3.index))

plt.figure(figsize=(12, 6))
plt.plot(ticks, [prey_sum1.get(t, 0) for t in ticks], label='scenariusz 1', color='blue')
plt.plot(ticks, [prey_sum2.get(t, 0) for t in ticks], label='scenariusz 2', color='green')
plt.plot(ticks, [prey_sum3.get(t, 0) for t in ticks], label='Scenariusz 3', color='red')
plt.xlabel('Tick (co 50 kroków w generacji)')
plt.ylabel('Suma populacji Zwierzyny (wszystkie generacje)')
plt.title('Porównanie sumarycznej liczby osobników Zwierzyny dla różnych scenariuszy')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
