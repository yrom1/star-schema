- [ ] Check strava inserts, I think there's a timezone issue
- [ ] Change timezone to est:
```mysql> SELECT @@global.time_zone, @@session.time_zone;
+--------------------+---------------------+
| @@global.time_zone | @@session.time_zone |
+--------------------+---------------------+
| UTC                | UTC                 |
+--------------------+---------------------+
1 row in set (0.05 sec)```
