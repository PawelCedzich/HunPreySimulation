import pandas as pd
import matplotlib.pyplot as plt

# Wczytaj dane
df = pd.read_csv("simulation_stats3.csv")

# Sprawdź, czy kolumna 'BestPreyFit' i 'BestPredFit' istnieje
if 'BestPreyFit' not in df.columns or 'BestPredFit' not in df.columns:
    raise ValueError("Brak kolumny 'BestPreyFit' lub 'BestPredFit' w pliku simulation_stats.csv")

# Dla każdej generacji wybierz największą wartość BestPreyFit i BestPredFit
best_prey_per_gen = df.groupby('generation')['BestPreyFit'].max()
best_pred_per_gen = df.groupby('generation')['BestPredFit'].max()

# Ogranicz do pierwszych 50 generacji
best_prey_per_gen = best_prey_per_gen.iloc[:50]
best_pred_per_gen = best_pred_per_gen.iloc[:50]
generations = best_prey_per_gen.index

plt.figure(figsize=(10, 6))
plt.plot(generations, best_prey_per_gen.values, marker='o', color='green', label='Najlepsze Dopasowanie Zwierzyny')
plt.plot(generations, best_pred_per_gen.values, marker='s', color='red', label='Najlepsze Dopasowanie Drapieżnika')
plt.xlabel('Generacja')
plt.ylabel('Najlepszy fitness')
plt.title('Najlepszy fitness Zwierzyna i Drapieżnik w każdej generacji')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
