import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# 1. Build the database fresh every run
conn = sqlite3.connect("flag_football.db")
conn.executescript("""
DROP TABLE IF EXISTS plays1;
DROP TABLE IF EXISTS games1;

CREATE TABLE games1 (
    game_id INTEGER PRIMARY KEY,
    game_date TEXT,
    opponent TEXT,
    points_for INTEGER,
    points_against INTEGER,
    weather TEXT
);

CREATE TABLE plays1 (
    play_id INTEGER PRIMARY KEY,
    game_id INTEGER,
    play_number INTEGER,
    quarter INTEGER,
    possession TEXT,
    down INTEGER,
    yards_to_go INTEGER,
    play_type TEXT,
    route TEXT,
    pass_depth TEXT,
    yards_gained INTEGER,
    result TEXT,
    first_down INTEGER,
    qb_gender TEXT,
    target_gender TEXT,
    coed_rule TEXT,
    FOREIGN KEY (game_id) REFERENCES games1(game_id)
);
""")


pd.read_csv("games1.csv").to_sql("games1", conn, if_exists="append", index=False)
pd.read_csv("plays1.csv").to_sql("plays1", conn, if_exists="append", index=False)

# routes
by_route = pd.read_sql("""
    SELECT route,
           COUNT(*) AS attempts,
           ROUND(AVG(CASE WHEN result IN ('complete','TD') THEN 1.0 ELSE 0 END), 2) AS completion_rate,
           ROUND(AVG(yards_gained), 2) AS avg_yards_per_attempt,
           ROUND(AVG(first_down), 2) AS first_down_rate
    FROM plays1
    WHERE play_type = 'pass'
    GROUP BY route
    ORDER BY avg_yards_per_attempt DESC
""", conn)
print(by_route, "\n")

# open vs closed
by_rule = pd.read_sql("""
    SELECT coed_rule,
           COUNT(*) AS attempts,
           ROUND(AVG(CASE WHEN result IN ('complete','TD') THEN 1.0 ELSE 0 END), 2) AS completion_rate,
           ROUND(AVG(yards_gained), 2) AS avg_yards_per_attempt
    FROM plays1
    WHERE play_type = 'pass'
    GROUP BY coed_rule
""", conn)
print(by_rule)

# visuals
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

axes[0].bar(by_route["route"], by_route["avg_yards_per_attempt"])
axes[0].set_title("Avg yards per attempt by route")
axes[0].set_ylabel("Yards")

axes[1].bar(by_route["route"], by_route["completion_rate"])
axes[1].set_title("Completion rate by route")
axes[1].set_ylim(0, 1)

axes[2].bar(by_rule["coed_rule"], by_rule["avg_yards_per_attempt"])
axes[2].set_title("Avg yards per attempt: open vs. closed")

plt.tight_layout()
plt.savefig("flag_football_charts.png")
plt.show()

closed_routes = pd.read_sql("""
SELECT route, coed_rule,
       COUNT(*) AS attempts,
       ROUND(AVG(yards_gained), 2) AS avg_yards,
       ROUND(AVG(first_down), 2) AS first_down_rate
FROM plays
WHERE play_type = 'pass'
GROUP BY route, coed_rule
ORDER BY route, coed_rule;
""", conn)
print("\nClosed plays only:")
print(closed_routes)

conn.close()