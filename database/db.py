import sqlite3

def db_setup():
    con = sqlite3.connect("Roles.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS welcome(emoji, role_name)")
    cur.execute("CREATE TABLE IF NOT EXISTS gaming(emoji, role_name)")
    return cur, con

def get_row_by_role(table, role):
    cur, con = db_setup()
    res = cur.execute(f'SELECT * FROM {table} WHERE role_name=\'{role}\'')
    data = res.fetchone()
    if(data is None):
        print("role not found")
    print(data)
    return data

def get_row_by_emoji(table, emoji):
    cur, con = db_setup()
    res = cur.execute(f'SELECT * FROM {table} WHERE emoji=\'{emoji}\'')
    data = res.fetchone()
    if(data is None):
        print("role not found")
    print(data)
    return data

def add_row(table, emoji, role):
    cur, con = db_setup()
    cur.execute(f'INSERT INTO {table} VALUES (\'{emoji}\', \'{role}\')')
    con.commit()

def remove_row(table, emoji):
    cur, con = db_setup()
    cur.execute(f'DELETE FROM {table} WHERE emoji=\'{emoji}\'')
    con.commit()

def get_table(table):
    cur, con = db_setup()
    res = cur.execute(f'SELECT * FROM {table}')
    data = res.fetchall()
    if(data is None):
        print("role not found")
    return data

