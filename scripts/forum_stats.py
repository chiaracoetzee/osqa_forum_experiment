#!/usr/bin/python
# -*- coding: utf-8 -*-
# Based on http://zetcode.com/db/postgresqlpythontutorial/
# Must be run as user postgres

import psycopg2
import sys
import numpy
import scipy.stats
from pychart import *

theme.get_options()
theme.output_file = '/tmp/test.eps'
data = [(10, 20, 30, 5)]
chart_object.set_defaults(area.T, size = (150, 120), y_range = (0, None),
                          x_coord = category_coord.T(data, 0))
chart_object.set_defaults(bar_plot.T, data = data)
ar = area.T(x_axis=axis.X(label="X label", format="/a-30{}%d"),
            y_axis=axis.Y(label="Y label", tic_interval=10))
ar.add_plot(bar_plot.T(label="foo", cluster=(0, 1)))
ar.draw()

con = None

def describe(x):
    print("mean: " + str(numpy.mean(x)) + ", stddev: " + str(numpy.std(x)))
    print("normaltest: " + str(scipy.stats.normaltest(x)))
    for dist in ['norm', 'expon', 'logistic', 'gumbel', 'extreme1']:
        print("anderson(" + dist + "): " + str(scipy.stats.anderson(x, dist)))

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

        query = "SELECT COUNT(anon_uid) as num_students, questions_viewed FROM " + \
                "    (SELECT anon_uid, COUNT(question_num) AS questions_viewed FROM " + \
                "        (SELECT DISTINCT anon_uid,regexp_replace(url_path, '/questions/([0-9]+).*', E'\\\\1') AS question_num " + \
                "         FROM monitored_actions " + \
                "         WHERE url_path ~ '/questions/[0-9]+.*') AS viewed_questions " + \
                "     GROUP BY anon_uid) AS questions_viewed_counts " + \
                "GROUP BY questions_viewed ORDER BY questions_viewed;"
        cur.execute(query)
        rows = cur.fetchall()
        print("number of questions viewed | number of students")
        result = ""
        total = 0
        count_list = []
        for row in rows:
            result = result + str(row[1]) + " | " + str(row[0]) + "\n"
            total = total + row[0]
            count_list += [row[1]] * row[0]
        count_list += [0] * (consented_count - total)
        sys.stdout.write("0 | " + str(consented_count - total) + "\n" + result)
        describe(count_list)
        print("")
        num_questions_viewed_count_list = count_list

        cur.execute("SELECT id, title, state_string, added_at FROM forum_node WHERE parent_id IS NULL")
        response_histogram = dict()
        max_responses = 0
        hours_to_first_response = []
        rows = cur.fetchall()
        for row in rows:
            parent_id = row[0]
            title = row[1]
            deleted = (row[2] == '(deleted)')
            question_added_at = row[3]
            if deleted:
                continue
            cur_responses = con.cursor()
            cur_responses.execute("SELECT COUNT(*), MIN(added_at) AS first_response_time FROM forum_node WHERE parent_id=" + str(parent_id))
            response_stats = cur_responses.fetchone()
            response_count = response_stats[0]
            first_response_added_at = response_stats[1]
            if response_count > 0:
                hours_to_first_response.append((first_response_added_at - question_added_at).seconds/60.0/60.0)
            if response_count not in response_histogram:
                response_histogram[response_count] = 1
            else:
                response_histogram[response_count] += 1
            max_responses = max(max_responses, response_count)
            # print title + (' (DELETED)' if deleted else '') + ": " + str(response_count)

        print("number of responses | number of questions with this number of responses")
        count_list = []
        for i in range(0, max_responses+1):
            if i in response_histogram:
                print str(i) + " " + str(response_histogram[i])
                count_list += [i] * response_histogram[i]
            else:
                print str(i) + " " + str(0)
        num_responses_count_list = count_list

        describe(count_list)
        print("")

        print("hours to first response: ")
        describe(hours_to_first_response)
        print("")
        return {'num_questions_viewed': [int(i) for i in num_questions_viewed_count_list],
                'num_responses': [int(i) for i in num_responses_count_list],
                'hours_to_first_response': hours_to_first_response}

    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)

    finally:
        if con:
            con.close()

print("Forum A:")
stats_a = dump_stats('cs1691x-a')
print("")
print("Forum B:")
stats_b = dump_stats('cs1691x-b')

for x in stats_a.keys():
    print('t-test on ' + x + ': ' + str(scipy.stats.ttest_ind(stats_a[x], stats_b[x])))
    print('K-S 2-sample test on ' + x + ': ' + str(scipy.stats.ks_2samp(stats_a[x], stats_b[x])))
    print('Mann-Whitney rank test on ' + x + ': ' + str(scipy.stats.mannwhitneyu(stats_a[x], stats_b[x])))
    print('')
