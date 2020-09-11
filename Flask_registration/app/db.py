import psycopg2

connection = psycopg2.connect(user="postgres",password="1234",host="127.0.0.1",port=5432,database="zen")
cursor = connection.cursor()

account = ("""CREATE TABLE IF NOT EXISTS "member"
(
    "id" SERIAL,
    "fullname" character varying(40) NOT NULL,
    "email" character varying(50) NOT NULL,
    "password" text NOT NULL,
    "address" text,
    PRIMARY KEY ("email")
);""")

cursor.execute(account)
connection.commit()
finally:
    cursor.close()
    connection.close()