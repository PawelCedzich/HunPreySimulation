import pandas as pd
import matplotlib.pyplot as plt

# Wczytaj dane z trzech plików
df1 = pd.read_csv("simulation_stats.csv")
df2 = pd.read_csv("simulation_stats2.csv")
df3 = pd.read_csv("simulation_stats3.csv")

# Sprawdź, czy kolumna 'BestPreyFit' istnieje
for i, df in enumerate([df1, df2, df3], 1):
    if 'BestPreyFit' not in df.columns:
        raise ValueError(f"Brak kolumny 'BestPreyFit' w pliku simulation_stats{i}.csv")

# Dla każdej generacji wybierz największą wartość BestPreyFit
best_prey_1 = df1.groupby('generation')['BestPreyFit'].max()
best_prey_2 = df2.groupby('generation')['BestPreyFit'].max()
best_prey_3 = df3.groupby('generation')['BestPreyFit'].max()

# Ogranicz do pierwszych 50 generacji (jeśli chcesz)
best_prey_1 = best_prey_1.iloc[:50]
best_prey_2 = best_prey_2.iloc[:50]
best_prey_3 = best_prey_3.iloc[:50]

# Wygładź wykresy za pomocą średniej kroczącej (rolling mean)
window = 5
best_prey_1_smooth = best_prey_1.rolling(window, min_periods=1).mean()
best_prey_2_smooth = best_prey_2.rolling(window, min_periods=1).mean()
best_prey_3_smooth = best_prey_3.rolling(window, min_periods=1).mean()

generations_1 = best_prey_1.index
generations_2 = best_prey_2.index
generations_3 = best_prey_3.index

plt.figure(figsize=(10, 6))
plt.plot(generations_1, best_prey_1_smooth.values, marker='o', color='blue', label='simulation_stats.csv')
plt.plot(generations_2, best_prey_2_smooth.values, marker='s', color='green', label='simulation_stats2.csv')
plt.plot(generations_3, best_prey_3_smooth.values, marker='^', color='red', label='simulation_stats3.csv')
plt.xlabel('Generacja')
plt.ylabel('Najlepszy fitness Zwierzyny (średnia krocząca)')
plt.title('Porównanie najlepszego fitnessu Zwierzyny (średnia krocząca, okno=5)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Sumaryczne zestawienie (najlepszy fitness w całym pliku)
print("Najlepszy fitness Zwierzyny w całym pliku:")
print(f"simulation_stats.csv:  {best_prey_1.max()}")
print(f"simulation_stats2.csv: {best_prey_2.max()}")
print(f"simulation_stats3.csv: {best_prey_3.max()}")
