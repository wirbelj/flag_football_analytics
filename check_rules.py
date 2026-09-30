import sqlite3
import pandas as pd

conn = sqlite3.connect("flag_football.db")

query = """
WITH prev AS (
    SELECT *,
           LAG(qb_gender)     OVER (PARTITION BY game_id ORDER BY play_number) AS prev_qb,
           LAG(target_gender) OVER (PARTITION BY game_id ORDER BY play_number) AS prev_target,
           LAG(yards_gained)  OVER (PARTITION BY game_id ORDER BY play_number) AS prev_yards,
           LAG(result)        OVER (PARTITION BY game_id ORDER BY play_number) AS prev_result,
           LAG(coed_rule)     OVER (PARTITION BY game_id ORDER BY play_number) AS prev_rule
    FROM plays
    WHERE possession = 'offense'
),
derived AS (
    SELECT play_number, coed_rule,
           CASE
               WHEN prev_qb = 'M' AND prev_target = 'M'
                    AND prev_result IN ('complete', 'TD') THEN 'closed'
               WHEN (prev_qb = 'F' OR prev_target = 'F')
                    AND prev_yards > 0 THEN 'open'
               ELSE prev_rule
           END AS derived_rule
    FROM prev
)
SELECT *
FROM derived
WHERE derived_rule IS NOT NULL
  AND derived_rule <> coed_rule;
"""

result = pd.read_sql(query, conn)
print(result)

conn.close()