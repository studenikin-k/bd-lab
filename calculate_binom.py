import sqlite3
import statistics
import math
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import List

connection = sqlite3.connect("movies.db")
db_cursor = connection.cursor()
db_cursor.execute("SELECT CAST(vote_count AS REAL), CAST(vote_average AS REAL),CAST(release_date AS TEXT) FROM movies WHERE vote_count IS NOT NULL AND vote_average IS NOT NULL")
data = db_cursor.fetchall()
connection.close()

vote_counts_list = [row[0] for row in data]
vote_averages_list = [row[1] for row in data]
release_dates = [row[2] for row in data]


def calculate_days(date_str: str, current_date: str = "2025-03-20") -> int:
    """Преобразует дату в формате YYYY-MM-DD в количество дней с текущей даты"""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    current = datetime.strptime(current_date, "%Y-%m-%d")
    delta = current - date
    return delta.days


def exponential_distribution(release_dates: List[str],
                             vote_counts: List[int],
                             current_date: str = "2025-03-20") -> None:
    """
    Строит график экспоненциального распределения F(Δt) = λ * e^(-λ * Δt)
    где λ = (сумма голосов) / (сумма дней)

    Args:
        release_dates: Список дат релизов в формате 'YYYY-MM-DD'
        vote_counts: Список количества голосов для каждого релиза
        current_date: Текущая дата для расчета (по умолчанию '2025-03-20')
    """
    if len(release_dates) != len(vote_counts):
        raise ValueError("Количество дат и голосов должно совпадать")

    # Рассчитываем общее количество дней и голосов
    total_days = sum(calculate_days(date, current_date) for date in release_dates)
    total_votes = sum(vote_counts)

    if total_days <= 0:
        raise ValueError("Общее количество дней должно быть положительным")

    # Рассчитываем общую λ
    lambda_ = total_votes / total_days

    # Создаем массив значений Δt для графика
    t = np.linspace(0, max(calculate_days(date, current_date) for date in release_dates), 1000)

    # Вычисляем значения функции распределения
    f_t = lambda_ * np.exp(-lambda_ * t)

    # Строим график
    plt.figure(figsize=(10, 6))
    plt.plot(t, f_t, label=f"λ={lambda_:.4f}\nГолосов: {total_votes}\nДней: {total_days}")

    # Отмечаем точки фактических данных
    for i, (date, votes) in enumerate(zip(release_dates, vote_counts)):
        days = calculate_days(date, current_date)
        plt.scatter(days, lambda_ * np.exp(-lambda_ * days),
                    color='red', zorder=5)
        plt.text(days, lambda_ * np.exp(-lambda_ * days),
                 f" {votes} голосов", ha='left', va='center')

    plt.title("Экспоненциальное распределение активности\nF(Δt) = λ * e^(-λ * Δt)")
    plt.xlabel("Δt (дни с момента релиза)")
    plt.ylabel("Плотность вероятности F(Δt)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

exponential_distribution(release_dates, vote_counts_list, current_date="2024-03-20")

avg_vote_count = statistics.mean(vote_counts_list)
avg_vote_average = statistics.mean(vote_averages_list)

num_trials = round(avg_vote_count)
success_probability = avg_vote_average / 10

expected_value = num_trials * success_probability
variance = num_trials * success_probability * (1 - success_probability)
std_deviation = math.sqrt(variance)

lower_k = max(0, int(expected_value - 3 * std_deviation))
upper_k = min(num_trials, int(expected_value + 3 * std_deviation))
k_values = list(range(lower_k, upper_k + 1))
binom_pmf = [math.exp(math.lgamma(num_trials+1)-math.lgamma(k+1)-math.lgamma(num_trials-k+1)+k*math.log(success_probability)+(num_trials-k)*math.log(1-success_probability)) for k in k_values]

print("Параметры биноминального распределения:")
print("num_trials =", num_trials)
print("success_probability =", success_probability)
print("expected_value =", expected_value)
print("std_deviation =", std_deviation)
print("Диапазон k:", k_values)
print("Вероятностная функция:")
for k, prob in zip(k_values, binom_pmf):
    print("k =", k, "P =", prob)

plt.figure(figsize=(10,6))
plt.bar(k_values, binom_pmf, color='blue')
plt.title("Биноминальное распределение")
plt.xlabel("k")
plt.ylabel("P(X=k)")
plt.savefig("binom_distribution.png")
plt.close() 