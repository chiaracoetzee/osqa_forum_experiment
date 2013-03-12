#!/bin/sh

if [ $# != 2 ]; then
    echo "please enter a DB, and the Django user for that DB"
    exit 1
fi

export DB=$1
export DJANGO_USER=$2

DIRPATH=`pwd`/`dirname $0`

psql \
    -X \
    -f $DIRPATH/setup_monitor_tb.sql \
    --echo-all \
    --single-transaction \
    --set AUTOCOMMIT=off \
    --set ON_ERROR_STOP=on \
    --set DJANGO_USER=\"$DJANGO_USER\" \
    $DB

psql_exit_status=$?

if [ $psql_exit_status != 0 ]; then
    echo "psql failed while trying to run this sql script" 1>&2
    exit $psql_exit_status
fi

echo "sql script successful"
exit 0
