import randomtimestamp
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
# 0-3 тега
# tag_nm, color_hex_code, person_id
cur_person_id = con.cursor()
enum = ["Утро", "День" , "Вечер", "Работа", "Учеба", \
        "Магазин", "Ноутбук", "Телефон", "Метро", "В пути"]
cur_person_id.execute("select person_id, created_dttm from prod.person")
cur = con.cursor()
for i in cur_person_id:
    person_id = i[0]
    person_created_dttm = i[1]
    enum_temp = enum.copy()
    i = 9
    for _ in range(random.randint(0, 3)):
        hex_code = faker.color()
        tag_nm = enum_temp[random.randint(0,i)]
        i -= 1
        enum_temp.remove(tag_nm)
        tag_created_dttm = randomtimestamp.randomtimestamp(start=person_created_dttm)
        cur.execute(
            f"""
                insert into prod.tag(tag_nm, color_hex_code, person_id, created_dttm)
                values ('{tag_nm}', '{hex_code}','{person_id}', '{tag_created_dttm}')
                """
        )
    con.commit()
con.close()
print('Done')