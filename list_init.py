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
# 1 папка на человека
# 3 списка на человека
# на каждый список по 20-40 задач рандомное число
cur_person_id = con.cursor()
# list: list_nm, color_hex_code, folder_id
# person_x_list: person_id, list_id, relation_type_nm ('OWNER')
cur_folder_id = con.cursor()
cur_folder_id.execute("""select folder_id from prod.folder""")
folders = list(cur_folder_id)
cur_person_id.execute("""select p.person_id from prod.person p""")
cur = con.cursor()
for i in cur_person_id:
    person_id = i[0]
    for num in range(random.randint(1, 3)):
        hex_code = faker.color()[1:]
        list_nm = faker.sentence(nb_words=random.randint(1,4))[:-1]
        relation_type_nm = 'OWNER'
        if person_id % 10 != 0 and person_id % 9 != 0 and person_id % 8 != 0:
            folder_id = folders[random.randint(0, len(folders) - 1)][0]
            cur.execute(
                f"""
                                insert into prod.list(list_nm, color_hex_code, folder_id)
                                values ('{list_nm}', '{hex_code}', '{folder_id}')
                             """
            )
        else:
            cur.execute(
                f"""
                    insert into prod.list(list_nm, color_hex_code)
                    values ('{list_nm}', '{hex_code}')
                 """
                )
        cur_list = con.cursor()
        cur_list.execute(f"""select max(list_id) from prod.list""")
        list_id_new = cur_list.fetchall()[0][0]
        cur.execute(
            f"""
                insert into prod.person_x_list(person_id, list_id, relation_type_nm)
                values ('{person_id}', '{list_id_new}', '{relation_type_nm}')
             """
            )
        con.commit()

con.close()
print('Done')