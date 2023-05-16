from faker import Faker
import psycopg2
import random

faker = Faker('ru_RU')


con = psycopg2.connect(
    dbname='postgres',
    user='postgres',
    password='root',
    host='127.0.0.1',
    port='5432'
)
cur_person_id = con.cursor()

cur_person_id.execute("select person_id from prod.person")
cur = con.cursor()
for i in cur_person_id:
    person_id = i[0]
    if person_id % 10 != 0 and person_id % 9 != 0 and person_id % 8 != 0:
        folder_nm = faker.sentence(nb_words=random.randint(1,3))[:-1]
        cur.execute(
            f"""
                insert into prod.folder(folder_nm)
                values ('{folder_nm}')
             """
        )
        con.commit()
con.close()
print('Done')