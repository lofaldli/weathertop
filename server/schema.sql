drop table if exists entries;
create table entries (
    id integer primary key autoincrement,
    timestamp text not null,
    temperature integer not null
);
