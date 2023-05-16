import randomtimestamp
from faker import Faker
import psycopg2
import datetime

faker = Faker('ru_RU')

con = psycopg2.connect(
    dbname='postgres',
    user='postgres',
    password='root',
    host='127.0.0.1',
    port='5432'
)

cur = con.cursor()

i = 0
while i < 500:
    profile = faker.simple_profile()
    person_nm = profile['name']
    birth_dt = profile['birthdate']
    if birth_dt < datetime.date(1980, 1, 1) or birth_dt > datetime.date(2012, 12, 1):
        continue
    email = profile['mail']
    created_dttm = randomtimestamp.randomtimestamp(start_year=2022)
    i += 1
    cur.execute(
        f"""
        insert into prod.person(person_nm, birth_dt, email)
        values ('{person_nm}', '{birth_dt}', '{email}')
        """
    )
    con.commit()
con.close()

