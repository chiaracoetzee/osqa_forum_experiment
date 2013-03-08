#!/bin/bash
for f in cs1692x cs1692x-a cs1692x-b; do sudo -u postgres dropdb $f; sudo -u postgres createdb -E utf8 -O $f $f; cd $f; chown -R osqa log; sudo -u osqa python manage.py syncdb; chown -R www-data log; cd ..; done
