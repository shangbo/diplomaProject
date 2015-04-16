create database request_spider
CHARACTER SET 'utf8'
COLLATE 'utf8_general_ci';
    use request_spider;
    create table requests
        (_id int not null auto_increment, 
         root varchar(200) not null, 
         _date DATETIME not null, 
         method varchar(10) not null, 
         url varchar(100) not null, 
         keys_values varchar(2000) not null, 
         md5 varchar(100) not null,
         sql_injection int not null,
         primary key(_id)
         )engine=INNODB DEFAULT CHARSET=utf8;