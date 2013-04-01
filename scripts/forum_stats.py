#!/usr/bin/python
# -*- coding: utf-8 -*-
# Based on http://zetcode.com/db/postgresqlpythontutorial/
# Must be run as user postgres

import psycopg2
import sys

con = None

def dump_stats(database):
    print('')
    try:
        con = psycopg2.connect(database=database, user='postgres') 
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM forum_user")
        registered_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM forum_user WHERE completed_consent=TRUE")
        consented_count = cur.fetchone()[0]
        print(str(consented_count) + " users consented of " + str(registered_count) + " registered users (" + str(100.0*consented_count/registered_count) + "%)")

        cur.execute("SELECT id, title, state_string FROM forum_node WHERE parent_id IS NULL")
        response_histogram = dict()
        max_responses = 0
        rows = cur.fetchall()
        for row in rows:
            parent_id = row[0]
            title = row[1]
            deleted = (row[2] == '(deleted)')
            if deleted:
                continue
            cur_responses = con.cursor()
            cur_responses.execute("SELECT COUNT(*) FROM forum_node WHERE parent_id=" + str(parent_id))
            response_count = cur_responses.fetchone()[0]
            if response_count not in response_histogram:
                response_histogram[response_count] = 1
            else:
                response_histogram[response_count] += 1
            max_responses = max(max_responses, response_count)
            print title + (' (DELETED)' if deleted else '') + ": " + str(response_count)

        for i in range(0, max_responses+1):
            if i in response_histogram:
                print str(i) + " " + str(response_histogram[i])
            else:
                print str(i) + " " + str(0)

    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)

    finally:
        if con:
            con.close()

dump_stats('cs1691x-a')
dump_stats('cs1691x-b')
