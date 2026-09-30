import pandas as pd
import sqlite3

conn = sqlite3.connect("flag_football.db")


conn.executescript("""
CREATE TABLE IF NOT EXISTS games1 (
    game_id INTEGER PRIMARY KEY,
    game_date TEXT,
    opponent TEXT,
    points_for INTEGER,
    points_against INTEGER,
    weather TEXT
);


CREATE TABLE IF NOT EXISTS plays1 (
    play_id INTEGER PRIMARY KEY,
    game_id INTEGER,
    play_number INTEGER,
    quarter INTEGER,
    possession TEXT,
    down INTEGER,
    yards_to_go INTEGER,
    play_type TEXT,
    yards_gained INTEGER,
    result TEXT,
    first_down INTEGER,
    qb_gender TEXT,
    target_gender TEXT,
    coed_rule TEXT,
    FOREIGN KEY (game_id) REFERENCES games1(game_id)
);
""")

plays = pd.read_csv("plays1.csv")
plays.to_sql("plays1", conn, if_exists="append", index=False)



conn.commit()
conn.close()