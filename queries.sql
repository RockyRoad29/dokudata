-- Homonym nodes are a cause of confusion
select type, name, count(*)
from nodes
group by type, name
having count(*) > 1;

-- Sorting nodes by name should help to understand problems
drop view if exists overview;
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