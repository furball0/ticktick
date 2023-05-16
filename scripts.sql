--1
--Вывести топ 10 пользователей (ФИО, количество задач)
--у которых больше всего задач с тегом "Учеба"
select p.person_id, p.person_nm, count(1)
  from prod.task t
       inner join prod.person_x_list pxl
               on t.list_id = pxl.list_id
              and pxl.relation_type_nm = 'OWNER'
       inner join prod.person p
               on pxl.person_id = p.person_id
       inner join prod.task_x_tag txt
               on txt.task_id = t.task_id
       inner join prod.tag tg
               on txt.tag_id = tg.tag_id
              and tg.tag_nm = 'Учеба'
group by 1
order by 3 desc
limit 10;


-- 2
-- Вывести количество задач пользователей по каждому из их тегов.
-- (ФИО + тег + количество задач на этот тег)
select p.person_id, tg.tag_id, p.person_nm, tg.tag_nm, count(1)
  from prod.task t
       inner join prod.person_x_list pxl
               on t.list_id = pxl.list_id
              and pxl.relation_type_nm = 'OWNER'
       inner join prod.person p
               on pxl.person_id = p.person_id
       inner join prod.task_x_tag txt
               on txt.task_id = t.task_id
       inner join prod.tag tg
               on txt.tag_id = tg.tag_id
group by 1, 2
order by 3, 5 desc;

-- 3
-- Вывести топ 10 пользователей по количеству задач за все время
select p.person_id,
	   p.person_nm,
       count(1) as task_cnt
  from prod.task t
       inner join prod.person_x_list pxl
               on t.list_id = pxl.list_id
              and pxl.relation_type_nm = 'OWNER'
       inner join prod.person p
               on pxl.person_id = p.person_id
 group by 1
 order by 3 desc
 limit 10;

-- 4
-- Вывести сделанные в июле 2022 задачи по всем людям
-- Вывести идентификатор задачи, название задачи, время выполнения задачи,
select t.task_id,
       t.task_nm,
       t.completed_by_person_id,
       t.actual_end_dttm - t.created_dttm as lead_time
  from prod.task t
 where actual_end_dttm between '2022-06-01' and '2022-07-01'
order by 4;

-- 5
-- Вывести по каждому пользователю общие метрики , среднее время выполнения задач, количество задач, за третий квартал 2022 года
with tmp as
(select p.person_id,
       avg(t.actual_end_dttm - t.created_dttm) as avg_lead_time,
       count(1) as task_cnt
  from prod.task t
       inner join prod.person_x_list pxl
               on t.list_id = pxl.list_id
              and pxl.relation_type_nm = 'OWNER'
       inner join prod.person p
               on pxl.person_id = p.person_id
 where t.completed_flg = true
   and t.actual_end_dttm between '2022-07-01' and '2022-09-30'
 group by 1)
select p.person_nm,
       t.avg_lead_time,
       t.task_cnt
  from prod.person p
       inner join tmp t
               on p.person_id = t.person_id
 order by 3 desc
 limit 10
;

-- 6
-- Вывести среднее время , через которое пользователь создает вторую задачу после создания первой задачи.
-- Добавить поле с case when: меньше 5 дней, 6-10 дней, 11-20 дней, больше 20 дней
-- Посчитать распределение этого case when
with first_task_create as (
select p.person_id,
       min(t.created_dttm) as first_task_created_dttm
  from prod.task t
       inner join prod.person_x_list pxl
               on t.list_id = pxl.list_id
              and pxl.relation_type_nm = 'OWNER'
       inner join prod.person p
               on pxl.person_id = p.person_id
  group by 1
),
tmp as (
select ftc.person_id,
       min(t.created_dttm - ftc.first_task_created_dttm) as dif_time
  from prod.task t
       inner join prod.person_x_list pxl
               on t.list_id = pxl.list_id
              and pxl.relation_type_nm = 'OWNER'
       inner join first_task_create ftc
               on pxl.person_id = ftc.person_id
where t.created_dttm != ftc.first_task_created_dttm
  group by 1)
select case when dif_time < '5 day'::interval then 'Меньше 5 дней' else
            case when dif_time < '10 day'::interval then '6 - 10 Дней' else
                case when dif_time < '20 day'::interval then '11 - 20 Дней' else
                    'Больше 20 дней' end end end as dif_time_code,
       count(1) as cnt
  from tmp
 group by 1
 order by 2 desc
;

-- 7
-- Вывести, какое количество задач в среднем люди делают в первый месяц после создания первой задачи, во второй месяц и так далее,
-- средние значения.
with first_task_create as (
select p.person_id,
       min(t.created_dttm) as first_task_created_dttm
  from prod.task t
       inner join prod.person_x_list pxl
               on t.list_id = pxl.list_id
              and pxl.relation_type_nm = 'OWNER'
       inner join prod.person p
               on pxl.person_id = p.person_id
  group by 1
)
select round(extract(epoch from t.actual_end_dttm - ftc.first_task_created_dttm) / 2629746 + 1) as month,
       count(1)
  from prod.task t
       inner join prod.person_x_list pxl
               on t.list_id = pxl.list_id
              and pxl.relation_type_nm = 'OWNER'
       inner join first_task_create ftc
               on pxl.person_id = ftc.person_id
 where t.completed_flg = true
 group by 1
 order by 1
limit 12;

-- 8
-- Вывести самый длинный / короткий промежуток времени между выполнениями задач для каждого пользователя
-- (+ их количество задачи и средний промежуток между выполнением задач).
with lag_tmp as (
select p.person_id,
       p.person_nm,
       t.task_id,
       t.actual_end_dttm as end_dttm,
       lag(t.actual_end_dttm) over
           (partition by p.person_id order by t.actual_end_dttm)
           as lag_end_dttm
  from prod.task t
       inner join prod.person_x_list pxl
               on t.list_id = pxl.list_id
              and pxl.relation_type_nm = 'OWNER'
       inner join prod.person p
               on pxl.person_id = p.person_id
 where t.completed_flg = true
 )
select t.person_id,
       t.person_nm,
       count(1) as tasks_cnt,
       min(t.end_dttm - t.lag_end_dttm) as min_dif_between_tasks_time,
       max(t.end_dttm - t.lag_end_dttm) as max_dif_between_tasks_time,
       avg(t.end_dttm - t.lag_end_dttm) as avg_dif_between_tasks_time
  from lag_tmp t
 where t.lag_end_dttm is not null
 group by 1, 2
order by 1;

-- 9
-- Вывести топ 10 по количеству завершенных привычек пользователей
select p.person_id,
       p.person_nm,
       count(1) filter (where h.completed_flg = true) as compeleted_habits_count,
       count(1) as habits_count
  from prod.habit h
       inner join prod.person p
               on h.person_id = p.person_id
 group by 1, 2
 order by 3 desc
 limit 10
;

-- 10
-- Вывести список топ 10 пользователей (ФИО + количество), оставивших больше всех комментариев к задачам
with tmp as (
select p.person_id,
       person_nm,
       count(1) as comment_cnt
  from prod.comment c
       inner join prod.task t
               on c.task_id = t.task_id
       inner join prod.person_x_list pxl
               on t.list_id = pxl.list_id
              and pxl.relation_type_nm = 'OWNER'
       inner join prod.person p
               on pxl.person_id = p.person_id
 group by 1
 order by 3 desc
 limit 10)
select person_nm, comment_cnt from tmp;