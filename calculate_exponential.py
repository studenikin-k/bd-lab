import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import List


def get_movie_data(db_path: str = "movies.db") -> tuple:
    """Получает данные о фильмах из базы данных"""
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT CAST(vote_count AS REAL), 
               CAST(vote_average AS REAL),
               CAST(release_date AS TEXT) 
        FROM movies 
        WHERE vote_count IS NOT NULL 
          AND vote_average IS NOT NULL
          AND release_date IS NOT NULL
    """)

    data = cursor.fetchall()
    connection.close()

    vote_counts = [row[0] for row in data]
    vote_averages = [row[1] for row in data]
    release_dates = [row[2] for row in data]

    return vote_counts, vote_averages, release_dates


def calculate_days(release_date: str, current_date: str = "2025-03-20") -> int:
    """Вычисляет количество дней с момента релиза до текущей даты"""
    try:
        release = datetime.strptime(release_date, "%Y-%m-%d")
        current = datetime.strptime(current_date, "%Y-%m-%d")
        return (current - release).days
    except ValueError:
        return None  # Для некорректных дат


def plot_movie_distributions(vote_counts: List[float],
                             release_dates: List[str],
                             current_date: str = "2025-03-20",
                             top_n: int = 20) -> None:
    """
    Строит экспоненциальные распределения для фильмов

    Args:
        vote_counts: Количество голосов для каждого фильма
        release_dates: Даты релизов в формате 'YYYY-MM-DD'
        current_date: Дата, от которой считаем дни
        top_n: Количество фильмов для отображения (по убыванию λ)
    """
    # Фильтруем данные и рассчитываем λ для каждого фильма
    movies_data = []
    for votes, date in zip(vote_counts, release_dates):
        days = calculate_days(date, current_date)
        if days is not None and days > 0 and votes > 0:
            λ = votes / days
            movies_data.append({
                'votes': votes,
                'days': days,
                'lambda': λ,
                'release_date': date
            })

    # Сортируем по убыванию λ (наиболее интенсивные первые)
    movies_data.sort(key=lambda x: x['lambda'], reverse=True)

    # Берем только top_n фильмов для визуализации
    if top_n > 0:
        movies_data = movies_data[:top_n]

    if not movies_data:
        print("Нет данных для визуализации")
        return

    # Создаем график
    plt.figure(figsize=(14, 8))
    max_days = max(m['days'] for m in movies_data)
    x_values = np.linspace(0, max_days * 1.1, 500)

    # Цветовая палитра для лучшей различимости
    colors = plt.cm.viridis(np.linspace(0, 1, len(movies_data)))

    for idx, movie in enumerate(movies_data):
        λ = movie['lambda']
        y_values = λ * np.exp(-λ * x_values)

        plt.plot(x_values, y_values,
                 color=colors[idx],
                 label=f"{movie['release_date']}\nλ={λ:.2f} ({movie['votes']:.0f} гол.)")

        # Текущая точка
        current_y = λ * np.exp(-λ * movie['days'])
        plt.scatter(movie['days'], current_y, color=colors[idx], zorder=5)

    plt.title(f"Топ-{len(movies_data)} фильмов по интенсивности голосования (λ)\nF(t) = λ·e^(-λt)")
    plt.xlabel("Дни с момента релиза")
    plt.ylabel("Плотность вероятности F(t)")
    plt.grid(True, alpha=0.2)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    # Добавляем дополнительную информацию
    plt.text(0.02, 0.95,
             f"Дата анализа: {current_date}\nВсего фильмов: {len(movies_data)}",
             transform=plt.gca().transAxes,
             bbox=dict(facecolor='white', alpha=0.8))

    plt.show()


# Основной процесс
if __name__ == "__main__":
    # 1. Получаем данные из БД
    vote_counts, vote_averages, release_dates = get_movie_data()

    # 2. Визуализируем распределения
    plot_movie_distributions(vote_counts, release_dates, top_n=15)