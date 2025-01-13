import sqlite3

emoji_to_role_welcome = [
    ('🎰', 'Daily Games'),
    ('🤪', 'Memes'),
    ('🤳', 'Tik Toks'),
    ('🖨️', '3D Printing'),
    ('🥞', 'Food'),
    ('<:Mario_Dab:1051627790887297044>', 'Gaming'),
    ('🎵', 'Music'),
    ('🧑‍💻', 'Game Dev'),
    ('📚', 'Books')
]

emoji_to_role_gaming = [
    ('🤬', 'LOL'),
    ('<:Mario_TPose:1051627791776497855>', 'SM64'),
    ('🔒', 'Deadlock'),
    ('🌫️', 'Enshrouded'),
    ('🃏', 'TCG'),
    ('🪝', 'POE')
]

def db_setup():
    con = sqlite3.connect("Roles.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS welcome(emoji, role_name)")
    cur.execute("CREATE TABLE IF NOT EXISTS gaming(emoji, role_name)")

    cur.executemany("INSERT INTO welcome VALUES(?, ?)", emoji_to_role_welcome)
    cur.executemany("INSERT INTO welcome VALUES(?, ?)", emoji_to_role_welcome)
    con.commit()

db_setup()