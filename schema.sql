/*
Fri Dec 23
mysql> ALTER TABLE dimension_strava
    -> MODIFY COLUMN distance_km FLOAT(4, 2);
Query OK, 0 rows affected, 1 warning (0.16 sec)
Records: 0  Duplicates: 0  Warnings: 1

mysql> ALTER TABLE dimension_leetcode
    -> ADD COLUMN submissions INT NOT NULL;
Query OK, 0 rows affected (0.06 sec)
Records: 0  Duplicates: 0  Warnings: 0

*/

START TRANSACTION;

CREATE DATABASE IF NOT EXISTS metrics;

USE metrics;

CREATE TABLE IF NOT EXISTS dimension_jira (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
    , issues_done INT NOT NULL
);

CREATE TABLE IF NOT EXISTS dimension_leetcode (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
    , python3_problems INT NOT NULL
    , mysql_problems INT NOT NULL
    , rank_ INT NOT NULL
    , streak INT NOT NULL
    , submissions INT NOT NULL
);

CREATE TABLE IF NOT EXISTS dimension_strava (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
    , distance_km FLOAT(4, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_table (
    date DATE NOT NULL PRIMARY KEY DEFAULT (CURRENT_DATE)
    , id_jira INT
    , id_leetcode INT
    , id_strava INT
    , FOREIGN KEY (id_jira) REFERENCES dimension_jira(id)
    , FOREIGN KEY (id_leetcode) REFERENCES dimension_leetcode(id)
    , FOREIGN KEY (id_strava) REFERENCES dimension_strava(id)
);

COMMIT;
