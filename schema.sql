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
);

CREATE TABLE IF NOT EXISTS dimension_strava (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
    , distance_km INT NOT NULL
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
