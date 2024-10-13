import sqlite3

loldle_db_con = sqlite3.connect("loldle.db")
loldle_db_cur = loldle_db_con.cursor()

def get_loldle_data(date, userId):
    res = loldle_db_cur.execute(f'SELECT * FROM loldle WHERE date={date} AND user_id={userId}')
    data = res.fetchone()
    print(data)
    return data

def add_loldle_data(date, userId, data):
    loldle_db_cur.execute(f"INSERT INTO loldle VALUES ('{date}', '{userId}', '{data}')")
    loldle_db_con.commit()