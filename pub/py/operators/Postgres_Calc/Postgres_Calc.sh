#!/bin/bash
sudo -u postgres psql $4 -c "DROP TABLE $3; "
sudo -u postgres psql $4 -c "CREATE TABLE $3 AS SELECT *, $2 FROM $1 ;"