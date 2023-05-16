import datetime

import randomtimestamp
from faker import Faker
import psycopg2
import random

import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Connection": "keep-alive",
}
url = "https://lifehacker.ru/203-privychki/"

# Send a GET request to the URL
response = requests.get(url, headers= headers)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

articles = soup.find_all("ol")

result_habit_name_list = []
for i, el in enumerate(articles):
    if i == 0:
        new_line = str(el)[5:]
    else:
        new_line = str(el).split(';"> ')[1]

    lst = new_line.split('</li> ')[:-1]

    result_habit_name_list.extend([x[4:] for x in lst])

print(result_habit_name_list)

faker = Faker('ru_RU')


con = psycopg2.connect(
    dbname='postgres',
    user='postgres',
    password='root',
    host='127.0.0.1',
    port='5432'
)

cur_person_id = con.cursor()

cur_person_id.execute("""select p.person_id from prod.person p""")
cur = con.cursor()
for i in cur_person_id:
    person_id = i[0]
    print(f"Person_id = {person_id}")
    person_created_dttm = i[1]
    for num in range(random.randint(0, 3)):
        habit_nm = result_habit_name_list[random.randint(0, len(result_habit_name_list)-1)]
        start_dt = randomtimestamp.random_date(start=person_created_dttm.date(), end=datetime.date(2023,1,1))
        repetition_freq = '1 day'
        goal_days_cnt = 30
        completed_flg = random.randint(0, 1)
        if completed_flg:
            completed_days_cnt = 30
            cur.execute(f"""
                        insert into prod.habit 
                        (habit_nm, person_id, start_dt, repetition_freq, goal_days_cnt,\
                         completed_days_cnt, completed_flg) values 
                         ('{habit_nm}','{person_id}','{start_dt}','{repetition_freq}',\
                         '{goal_days_cnt}','{completed_days_cnt}','{completed_flg}')
                        """)
        else:
            completed_days_cnt = random.randint(0, goal_days_cnt-1)
            cur.execute(f"""
                        insert into prod.habit 
                        (habit_nm, person_id, start_dt, repetition_freq, goal_days_cnt,\
                        completed_days_cnt, completed_flg) values 
                        ('{habit_nm}','{person_id}','{start_dt}','{repetition_freq}',\
                        '{goal_days_cnt}','{completed_days_cnt}','{completed_flg}')
                        """)
        cur_habit = con.cursor()
        cur_habit.execute(f"""select max(habit_id) from prod.habit""")
        habit_id_new = cur_habit.fetchall()[0][0]
        for k in range(completed_days_cnt):
            action_dttm = randomtimestamp.randomtimestamp(start=person_created_dttm)
            cur.execute(f"""
                        insert into prod.habit_action
                        (habit_id, action_dttm) values 
                        ('{habit_id_new}', '{action_dttm}')
                        """)
        con.commit()

con.close()
print('Done')