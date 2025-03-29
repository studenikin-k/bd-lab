import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import List
import os


def get_movie_data(db_path: str = "movies.db") -> tuple:
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
    release_dates = [row[2] for row in data]
    return vote_counts, release_dates


def calculate_hours(release_date: str, current_date: str = "2025-03-20") -> float:
    try:
        release = datetime.strptime(release_date, "%Y-%m-%d")
        current = datetime.strptime(current_date, "%Y-%m-%d")
        delta = current - release
        return delta.total_seconds() / 3600
    except ValueError:
        return None


def plot_movie_distributions(vote_counts: List[float],
                             release_dates: List[str],
                             current_date: str = "2025-03-20",
                             top_n: int = 20,
                             output_dir: str = "output") -> None:
    os.makedirs(output_dir, exist_ok=True)
    movies_data = []
    for votes, date in zip(vote_counts, release_dates):
        hours = calculate_hours(date, current_date)
        if hours is not None and hours > 0 and votes > 0:
            λ = votes / hours
            movies_data.append({'votes': votes, 'hours': hours, 'lambda': λ, 'release_date': date})
    movies_data.sort(key=lambda x: x['lambda'], reverse=True)
    movies_data = movies_data[:top_n]
    if not movies_data:
        print("Нет данных для визуализации")
        return

    plt.figure(figsize=(14, 8), dpi=200)
    colors = plt.cm.plasma(np.linspace(0, 1, len(movies_data)))

    for idx, movie in enumerate(movies_data):
        λ = movie['lambda']
        scaled_hours = movie['hours'] / 10000


        x = np.linspace(0, 8, 500)
        y = λ**-1 * np.exp(-x/λ)


        mask = y > 1e-5
        plt.plot(x[mask], y[mask], color=colors[idx], linewidth=2,
                 label=f"{movie['release_date']} (λ={λ:.2e}, Голоса: {movie['votes']:.0f})")


        plt.scatter([scaled_hours], [0], color=colors[idx], s=50, edgecolors='black', zorder=5)


        plt.plot([scaled_hours, scaled_hours], [0, λ * np.exp(-λ * scaled_hours)],
                 color=colors[idx], linestyle='dashed', linewidth=1)

    plt.title("Экспоненциальное распределение (ось X уменьшена в 10,000 раз)", fontsize=14)
    plt.xlabel("Часы после релиза (×10,000)", fontsize=12)
    plt.ylabel("Плотность вероятности", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='upper right', fontsize=7, frameon=False, ncol=2)
    plt.tight_layout()

    output_filename = f"exponential_distribution_{current_date}.png"
    output_path = os.path.join(output_dir, output_filename)
    plt.savefig(output_path, bbox_inches='tight')
    print(f"График сохранен: {output_path}")
    plt.close()


if __name__ == "__main__":
    vote_counts, release_dates = get_movie_data()
    plot_movie_distributions(vote_counts, release_dates, top_n=15)