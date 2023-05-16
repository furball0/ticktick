import datetime
import randomtimestamp
from faker import Faker
import psycopg2
import random

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Create a new instance of the WebDriver
driver = webdriver.Chrome('chromedrive.exe')
result_task_name_list = []
# Navigate to the URL
url = 'https://my.365done.ru/happiness'
driver.get(url)
for i in range(100):
    # Find and click the button
    button_xpath = '//*[@id="root"]/div/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/button'
    button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, button_xpath)))
    button.click()

    # Wait for the new page to load
    wait = WebDriverWait(driver, 5)
    page_content = driver.page_source

    soup = BeautifulSoup(page_content, "html.parser")
    # Perform further extraction or processing here
    lst = str(soup.find_all("div", {"class": "suggestions-picker"}))[33:-7]
    lst = lst.split('<a class="suggestions-picker__item" title="нажми, чтобы добавить в свой список">')[1:]
    result_task_name_list.extend([x[:-4] for x in lst])


driver.quit()

faker = Faker('ru_RU')


con = psycopg2.connect(
    dbname='postgres',
    user='postgres',
    password='root',
    host='127.0.0.1',
    port='5432'
)
cur_person_list_id = con.cursor()
priority = ['HIGH', 'MEDIUM', 'LOW']




cur_person_list_id.execute("select person_id, list_id from prod.person_x_list order by person_id")
cur = con.cursor()
for i in cur_person_list_id:
    person_id = i[0]
    print(person_id)
    list_id = i[1]
    for _ in range(random.randint(0, 100)):
        task_nm = result_task_name_list[random.randint(0, len(result_task_name_list)-1)]
        task_desc = faker.paragraph(nb_sentences=random.randint(0, 10))
        is_note_flg = 0
        priority_nm = priority[random.randint(0,2)]
        completed_flg = random.randint(0, 1)
        created_dttm = randomtimestamp.randomtimestamp()
        if completed_flg:
            actual_end_dttm = randomtimestamp.randomtimestamp(start=created_dttm)
            cur.execute(f"""
                insert into prod.task(task_nm, task_desc, is_note_flg, priority_nm, \
                                      actual_end_dttm, completed_flg, list_id, completed_by_person_id, created_dttm)
                values ('{task_nm}', '{task_desc}', '{is_note_flg}', '{priority_nm}', '{actual_end_dttm}', \
                        '{completed_flg}', '{list_id}', '{person_id}', '{created_dttm}')
            """)
        else:
            cur.execute(f"""
                            insert into prod.task(task_nm, task_desc, is_note_flg, priority_nm, \
                                                  completed_flg, list_id,  created_dttm)
                            values ('{task_nm}', '{task_desc}', '{is_note_flg}', '{priority_nm}', \
                                    '{completed_flg}', '{list_id}', '{created_dttm}')
                        """)
        con.commit()

        ### TASK_X_TAG
        cur_task_id = con.cursor()
        cur_task_id.execute(f"""select max(task_id) from prod.task""")
        task_id_new = cur_task_id.fetchall()[0][0]
        cur_tag = con.cursor()
        cur_tag.execute(f"""select tag_id from prod.tag where person_id = '{person_id}'""")
        tag_ids = cur_tag.fetchall()
        if len(tag_ids) > 0:
            tag_id = tag_ids[random.randint(0, len(tag_ids)-1)][0]
            task_x_tag_created_dttm = randomtimestamp.randomtimestamp(start=created_dttm)
            cur.execute(f"""insert into prod.task_x_tag (task_id, tag_id, created_dttm) 
                        values ('{task_id_new}', '{tag_id}', '{task_x_tag_created_dttm}')
                        """)
        ### COMMENT
        if random.randint(0, 1):
            comment_txt = faker.sentence(nb_words=random.randint(3, 25))[:-1]
            comment_created_dttm = randomtimestamp.randomtimestamp(start=created_dttm)
            cur.execute(f"""
                        insert into prod.comment (comment_txt, task_id, person_id, created_dttm)
                        values ('{comment_txt}', '{task_id_new}', '{person_id}', '{comment_created_dttm}')
                        """)
        ### TASK_X_SUBTASK
        num = random.randint(1, 10)
        if num >= 9:
            cur_task_x_subtask = con.cursor()
            cur_task_x_subtask.execute(f"""select task_id 
                                             from prod.task t 
                                                  inner join prod.person_x_list pxl 
                                                          on t.list_id = pxl.list_id
                                                         and pxl.relation_type_nm ='OWNER'
                                                         and person_id = '{person_id}'
                                        """)
            task_ids = cur_task_x_subtask.fetchall()
            if len(task_ids) > 0:
                task_id_owner = task_ids[random.randint(0, len(task_ids)-1)][0]
                task_x_subtask_created_dttm = randomtimestamp.randomtimestamp(start=created_dttm)
                cur.execute(f"""insert into prod.task_x_subtask (task_id, subtask_id, created_dttm) 
                                values ('{task_id_owner}', '{task_id_new}', '{task_x_subtask_created_dttm}')
                            """)
    con.commit()
con.close()
print('Done')