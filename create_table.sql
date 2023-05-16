-- Active: 1666634127988@@127.0.0.1@5432@postgres@prod

create type priority as enum ('HIGH', 'MEDIUM', 'LOW');
create type list_access_level as enum ('EDIT', 'COMMENT', 'READ', 'OWNER');

create schema prod;

create table prod.person
(
    person_id serial not null primary key,
    person_nm varchar(65),
    birth_dt date,
    email varchar(128)
);

create table prod.folder
(
    folder_id serial not null primary key,
    folder_nm varchar(65)
);

create table prod.list
(
    list_id serial not null primary key,
    list_nm varchar(65),
    color_hex_code varchar(7),
    folder_id int references prod.folder(folder_id)
);


create table prod.task
(
    task_id serial not null primary key,
    task_nm text,
    task_desc text,
    priority_nm priority,
    sheduled_start_dttm timestamp,
    sheduled_end_dttm timestamp,
    actual_end_dttm timestamp,
    reminder_dttm timestamp,
    repetition_freq interval,
    goal_days_cnt int,
    completed_days_cnt int,
    completed_flg boolean default 0::boolean,
    created_dttm timestamp default now() not null,
    list_id int references prod.list(list_id),
    completed_by_person_id int references prod.person(person_id)
);

create table prod.comment
(
    comment_id serial not null primary key,
    comment_txt text,
    task_id int references prod.task(task_id),
    person_id int references prod.person(person_id),
    created_dttm timestamp default now() not null
);


create table prod.tag
(
    tag_id serial not null primary key,
    tag_nm varchar(65),
    color_hex_code varchar(7),
    person_id int references prod.person(person_id)
);

create table prod.task_x_tag
(
    task_id int references prod.task(task_id),
    tag_id int references prod.tag(tag_id),
    PRIMARY KEY (task_id, tag_id)
);


create table prod.person_x_list
(
    person_id int references prod.person(person_id),
    list_id int references prod.list(list_id),
    relation_type_nm list_access_level,
    PRIMARY KEY (person_id, list_id)
);

create table prod.habit
(
    habit_id serial not null primary key,
    habit_nm varchar(65),
    person_id int references prod.person(person_id),
    start_dt date,
    repetition_freq interval,
    actual_reminder_tm time,
    goal_days_cnt int,
    completed_days_cnt int,
    completed_flg boolean default 0::boolean,
    archived_flg boolean default 0::boolean
);

create table prod.habit_action
(
    habit_action_id serial not null primary key,
    habit_id int references prod.habit(habit_id),
    action_dttm timestamp
);




