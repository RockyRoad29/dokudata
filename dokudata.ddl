    CREATE TABLE nodes (
            id integer primary key autoincrement,
            type varchar(10) not null,
            ns_id integer references ns(id),
            name varchar(255) not null,
            size integer,
            sz_changes integer,
            sz_indexed integer,
            sz_meta integer,
            meta text
            );
    CREATE TABLE ns (
            id integer primary key autoincrement,
            fullname varchar(255) unique not null);
    CREATE TABLE revisions (
            id integer primary key autoincrement,
            node_id integer references nodes(id),
            time varchar(255) not null,
            size integer,
            mode char(1),
            user vchar(25),
            name vchar(255),
            ip char(16),
            summary varchar(255),
            extra varchar(255)
            );

create view overview as
select ns.fullname,  N.id, N.type, N.name, N.size, N.sz_changes,
  N.sz_indexed, N.sz_meta, count(R.id) as rev_cnt
from nodes N
inner join ns on ns.id=N.ns_id
left join revisions R on R.node_id=N.id
group by ns.fullname, N.id, N.type, N.name, N.size, N.sz_changes,
  N.sz_indexed, N.sz_meta
order by N.name;
-- make sure you get the same row count as table nodes.
