#!/bin/bash
sudo -u postgres psql $5 -c "DROP TABLE $4; "
sudo -u postgres psql $5 -c "CREATE TABLE $4 AS SELECT * FROM $1 LEFT JOIN $2 ON $3 ;"