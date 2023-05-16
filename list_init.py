import randomtimestamp
from faker import Faker
import psycopg2
import random
# Здесь необходимо заполнить таблицы list party_x_list
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
cur_person_id_folder_id = con.cursor()
# list: list_nm, color_hex_code, folder_id
# person_x_list: person_id, list_id, relation_type_nm ('OWNER')

cur_person_id_folder_id.execute("""select p.person_id,f.folder_id, f.created_dttm, p.created_dttm from prod.person p
                                    left join prod.folder f on p.person_id=f.person_id
                                """)
cur = con.cursor()
for i in cur_person_id_folder_id:
    person_id = i[0]
    folder_id = i[1]
    folder_created_dttm = i[2]
    person_created_dttm = i[3]
    for num in range(random.randint(1, 3)):
        hex_code = faker.color()[1:]
        list_nm = faker.sentence(nb_words=random.randint(1,4))[:-1]
        relation_type_nm = 'OWNER'
        if folder_id is None:
            list_created_dttm = randomtimestamp.randomtimestamp(start=person_created_dttm)
            cur.execute(
                f"""
                    insert into prod.list(list_nm, color_hex_code, created_dttm)
                    values ('{list_nm}', '{hex_code}', '{list_created_dttm}')
                 """
                )
        else:
            list_created_dttm = randomtimestamp.randomtimestamp(start=folder_created_dttm)
            cur.execute(
                f"""
                                insert into prod.list(list_nm, color_hex_code, folder_id, created_dttm)
                                values ('{list_nm}', '{hex_code}', '{folder_id}','{list_created_dttm}')
                             """
            )
        cur_list = con.cursor()
        cur_list.execute(f"""select max(list_id) from prod.list""")
        list_id_new = cur_list.fetchall()[0][0]
        cur.execute(
            f"""
                insert into prod.person_x_list(person_id, list_id, relation_type_nm, created_dttm)
                values ('{person_id}', '{list_id_new}', '{relation_type_nm}', '{list_created_dttm}')
             """
            )
        con.commit()

con.close()
print('Done')