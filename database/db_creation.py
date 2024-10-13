import sqlite3

loldle_db_con = sqlite3.connect("dailyGames.db")
loldle_db_cur = loldle_db_con.cursor()
loldle_db_cur.execute("CREATE TABLE loldle(date, user_id, scores)")

