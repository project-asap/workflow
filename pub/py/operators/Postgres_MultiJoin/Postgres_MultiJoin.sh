#!/bin/bash
sudo -u postgres psql $5 -c "DROP TABLE $4; "
sudo -u postgres psql $5 -c "CREATE TABLE $4 AS SELECT $3 FROM $1 WHERE $2 ;"