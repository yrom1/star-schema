-- query for making the dot plot
-- basically a mysql version of what makes the colors in yrom1/flask
SELECT *
    , CASE
        WHEN j.issues_done >= 4 THEN 1
        WHEN j.issues_done = 3 THEN 0
        ELSE -1
    END j_score
FROM fact_table f
    INNER JOIN dimension_jira j
        ON f.id_jira = j.id
    -- inner join dimension_strava s
    --     on f.id_strava = s.id
    -- inner join dimension_leetcode l
    --     on f.id_leetcode = l.id
