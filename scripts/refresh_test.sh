#!/bin/bash
sudo -u postgres dropdb test
sudo -u postgres createdb -E utf8 -O test test
cd osqatest
chown -R osqa log
sudo -u osqa python manage.py syncdb
chown -R www-data log
cd ..
