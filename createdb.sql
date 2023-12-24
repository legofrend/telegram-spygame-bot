
create table location(
    id integer primary key,
    set_name varchar(255),
    lang varchar(2),
    location varchar(255),
    roles varchar(300),
    filename varchar(500),
    file_id varchar(255)
);


create table round(
    id integer primary key,
    admin_id integer,
    game_id varchar(255),
    round_nbr integer,
    started datetime,
    finished datetime,
    location_id integer,
    spy_id integer,
    winner_type varchar(12),
    details varchar(300),
    FOREIGN KEY(location_id) REFERENCES location(id)
);


create table log(
    datetime_stamp datetime,
    user_id integer,
    game_id varchar(255),
    action varchar(10)
);

