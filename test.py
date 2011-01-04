import sqlite3

conn = sqlite3.connect('./db.sqlite3')
c = conn.cursor()

c.execute("SELECT * FROM client")

for line in c:
	print(line)
	
c.execute("SELECT * FROM job")

for line in c:
	print(line)