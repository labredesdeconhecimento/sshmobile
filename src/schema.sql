drop table if exists users;
create table users (
  id integer primary key autoincrement,
  username string not null,
  encrypted_password string not null
);

insert into users (username, encrypted_password) values ("admin", "3c9909afec25354d551dae21590bb26e38d53f2173b8d3dc3eee4c047e7ab1c1eb8b85103e3be7ba613b31bb5c9c36214dc9f14a42fd7a2fdb84856bca5c44c2");
