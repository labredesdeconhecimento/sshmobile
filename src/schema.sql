drop table if exists users;
create table users (
  id integer primary key autoincrement,
  username string not null,
  encrypted_password string not null
);

insert into users (username, encrypted_password) values ("admin", "123");
