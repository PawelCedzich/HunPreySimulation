import pandas as pd
import matplotlib.pyplot as plt

# Wczytaj dane
df = pd.read_csv("simulation_stats3.csv")

# Filtruj tylko ticki co 50 (tak jak logowanie)
df_tick = df[df['tick'] % 50 == 0]

# Grupowanie po ticku: sumujemy liczebności dla każdego kroku (ticka) w generacji
prey_sum = df_tick.groupby('tick')['preys_alive'].sum()
predator_sum = df_tick.groupby('tick')['predators_alive'].sum()

# Oś X: ticki co 50
ticks = sorted(df_tick['tick'].unique())

plt.figure(figsize=(12, 6))
plt.plot(ticks, [prey_sum.get(t, 0) for t in ticks], label='Suma Zwierzyna', color='blue')
plt.plot(ticks, [predator_sum.get(t, 0) for t in ticks], label='Suma Drapieżnik', color='red')
plt.xlabel('Tick (co 50 kroków w generacji)')
plt.ylabel('Suma populacji (wszystkie generacje)')
plt.title('Sumaryczna liczba osobników Zwierzyny i Drapieżnika dla każdego 50-tego ticka generacji')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
