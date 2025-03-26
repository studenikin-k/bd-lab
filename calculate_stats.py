import sqlite3
import statistics
from platform import release
from datetime import datetime

conn = sqlite3.connect("movies.db")
cursor = conn.cursor()
cursor.execute("SELECT CAST(popularity AS REAL), CAST(vote_count AS REAL), CAST(vote_average AS REAL), CAST(release_date AS TEXT) FROM movies")
rows = cursor.fetchall()
conn.close()

popularity = [row[0] for row in rows if row[0] is not None]
vote_count = [row[1] for row in rows if row[1] is not None]
vote_average = [row[2] for row in rows if row[2] is not None]
release_date =[row[3] for row in rows if row[3] is not None]

current_day = ["2025-03-20"]


def convert_dates_to_days_precise(release_date: [str]) -> [int]:

    days_list = []
    base_date = datetime(1, 1, 1)

    for date_str in release_date:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            delta = date_obj - base_date
            days_list.append(delta.days)
        except ValueError:
            days_list.append(0)

    return days_list

days = convert_dates_to_days_precise(release_date)
current_date = convert_dates_to_days_precise(current_day)
print(release_date)
print(days)
print(current_date)

def get_stats(data):
    return min(data), max(data), statistics.mean(data), statistics.median(data), statistics.stdev(data)

stats_popularity = get_stats(popularity)
stats_vote_count = get_stats(vote_count)
stats_vote_average = get_stats(vote_average)

print("Popularity: min = {}, max = {}, mean = {:.2f}, median = {:.2f}, std = {:.2f}".format(*stats_popularity))
print("Vote Count: min = {}, max = {}, mean = {:.2f}, median = {:.2f}, std = {:.2f}".format(*stats_vote_count))
print("Vote Average: min = {}, max = {}, mean = {:.2f}, median = {:.2f}, std = {:.2f}".format(*stats_vote_average))


