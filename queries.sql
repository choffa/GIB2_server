/* Find all points and the id of the events that they belong 
 * including start points
 */
SELECT pid, eid, ST_AsText(point) AS point
FROM points NATURAL JOIN event_point
UNION ALL
SELECT pid, eid, ST_AsText(point) AS point
FROM points JOIN events ON pid = start_point_id
ORDER BY pid ASC;

/* Query for checking points within distance */
select pid, ST_AsText(point) as point, ST_Distance(point, ST_GeogFromText('POINT(63.4140397 10.4134941)')) as dist from points where dist < 200;
