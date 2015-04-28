create database request_spider
CHARACTER SET 'utf8'
COLLATE 'utf8_general_ci';
    use request_spider

    create table user_info
        (username varchar(50) not null,
         passwd varchar(50) not null,
         email varchar(50) not null default '',
         primary key(username)
        )engine=INNODB DEFAULT CHARSET=utf8;

    create table user_scan_record
        (_id int not null auto_increment,
         username varchar(50) not null,
         root varchar(200) not null,
         request_num int(8) default 400,
         thread_num int(8) default 10,
         connection_status int default 0,
         scan_status int default 0,
         sql_status int default 2,
         xss_status int default 2,
         cms_status int default 2,
         start_time DATETIME not null,
         end_time DATETIME,
         primary key(_id),
         foreign key(username) references user_info(username)
        )engine=INNODB DEFAULT CHARSET=utf8;

    create table requests
        (_id int not null auto_increment,
         username varchar(50) not null,
         root varchar(200) not null, 
         _date DATETIME not null, 
         method varchar(10) not null, 
         url varchar(100) not null, 
         keys_values varchar(2000) not null, 
         md5 varchar(100) not null,
         sql_injection int not null,
         primary key(_id),
         foreign key(username) references user_info(username)
         )engine=INNODB DEFAULT CHARSET=utf8;
