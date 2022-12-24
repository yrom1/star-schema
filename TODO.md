- [ ] Check strava inserts, I think there's a timezone issue
  - [x] Change timezone to est:
  ```
  mysql> SELECT @@global.time_zone, @@session.time_zone;
  +--------------------+---------------------+
  | @@global.time_zone | @@session.time_zone |
  +--------------------+---------------------+
  | UTC                | UTC                 |
  +--------------------+---------------------+
  1 row in set (0.05 sec)
  ```
  ```
  mysql>  SELECT @@global.time_zone;
  +--------------------+
  | @@global.time_zone |
  +--------------------+
  | US/Eastern         |
  +--------------------+
  1 row in set (0.04 sec)
  ```
  - [ ] Change timezone back to UTC on RDS
  - [ ] Maybe switch from primary key date to primary key `AUTO_INCREMENT` in `fact_table` and have `dimension_time` with `start_utc` `end_utc` with UTC datetimes indicating the start and end of the day for my EST/EDT timezone (but in UTC).
      - https://eranki.tumblr.com/post/27076431887/scaling-lessons-learned-at-dropbox-part-1 :
          - "Keep everything in UTC internally! Server times, stuff in the database, etc. This will save lots of headaches, and not just daylight savings time. Some software just doesn’t even handle non-UTC time properly, so don’t do it! We kept a clock on the wall set to UTC. When you want to display times to a user, make the timezone conversion happen at the last second."
  - [ ] Redo the time logic in the metric tracking repos. In the metric tracking repos for some reason I forced everything into ISO strings avoiding datetime objects:
      - https://www.bloomberg.com/company/stories/work-dates-time-python/
      - https://www.youtube.com/watch?v=XZlPXLsSU2U pycon us shows how to use the modern zoneinfo stuff
- [x] Pop quiz what's the highest value FLOAT(3, 2) can hold? It's 9.99, you'll need to fix the schema if you start running farther.
- [x] Get a smaller aws instance (I have the cheapest one and least storage, maybe (maybe) aws aurora is slightly cheaper although I'm unsure)
  - [ ] look more into rds pricing structure
  - [ ] transfer db, keep the same connection details?
