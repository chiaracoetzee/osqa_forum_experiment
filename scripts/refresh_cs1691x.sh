#!/bin/bash
for f in cs1691x cs1691x-a cs1691x-b; do sudo -u postgres dropdb $f; sudo -u postgres createdb -E utf8 -O $f $f; cd $f; chown -R osqa log; sudo -u osqa python manage.py syncdb; chown -R www-data log; cd ..; done
