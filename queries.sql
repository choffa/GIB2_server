/* Find all points and the id of the events that they belong 
 * including start points */
SELECT pid, eid, ST_AsText(point) AS point
FROM points NATURAL JOIN event_point
WHERE eid=16
UNION ALL
SELECT pid, eid, ST_AsText(point) AS point
FROM points JOIN events ON pid = start_point_id
WHERE eid=16
ORDER BY pid ASC;

/* Query for checking points within distance */
SELECT pid, point_text, dist
FROM (
    select pid, ST_AsText(point) as point_text, ST_Distance(point, ST_GeogFromText('POINT(63.4137739 10.412037)')) as dist from points
) AS sub_table
WHERE dist <= 200
ORDER BY dist ASC;

/* Query for checking events within distance */
SELECT eid, pid, point_text, dist
FROM (
    select eid, pid, ST_AsText(point) as point_text, ST_Distance(point, ST_GeogFromText('POINT(63.4137739 10.412037)')) as dist from points join events on start_point_id = pid
) AS sub_table
WHERE dist <= 200
ORDER BY dist ASC;