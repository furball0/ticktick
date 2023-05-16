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

cur_id = con.cursor()
cur_id.execute("""
                      select t.task_id, l.person_id
                        from prod.task t 
                             inner join prod.person_x_list l 
                                     on t.list_id = l.list_id
                                    and l.relation_type_nm = 'OWNER'
                """)
cur = con.cursor()
for i in cur_id:
    task_id = i[0]
    person_id = i[1]
    for _ in range(random.randint(0,1)):
        comment = faker.sentence(nb_words=random.randint(6,10))
        cur.execute(
            f"""
                insert into prod.comment(comment_txt, task_id, person_id)
                values ('{comment}', '{task_id}', '{person_id}')
                """
        )
    con.commit()
con.close()
print('Done')