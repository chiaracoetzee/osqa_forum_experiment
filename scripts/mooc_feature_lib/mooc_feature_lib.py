#!/usr/bin/python

'''
This python module implements a library of features to be extracted from the MOOC forum.
The intent is that any script in need of features should be able to ask this library for
the required feature, and this module will access the database to retrieve the feature for
all the students/forum-threads.

The features currently implemented are:
-

The features currently in progress of implementation are:
- Number of questions asked for each student

The features that need to be implemented are:
- Number of answers posted for each student
- Number of overall posts for each student
- Number of posts viewed for each student
- Number of upvotes/downvotes for each student
- Whether each student modified their profile
- Average time between posts for each student
'''

import psycopg2
import sys
from AnonymizerClient import AnonymizerClient

# This variable sets the database (the forum) to grab data from
# It must be set by the user before executing any other function
database = None
student_id_map = {}
ANON_PORT_NUM = 5000

'''
Set the map from anonymous student id to a fixed index from 0 upto
num_students-1. Even though this is called everytime this library
is used, it should be fixed and consistent once the number of students in the
class is fixed.
'''
def setStudentMap(db=database):
    try: 
        conn = psycopg2.connect(database=db, user='postgres')
        cur = conn.cursor()
        cur.execute("SELECT id FROM auth_user ORDER BY id")
        client = AnonymizerClient(ANON_PORT_NUM)
        for i, rec in enumerate(cur):
            anon_id = client.anonymize(int(rec[0]))
            student_id_map[anon_id] = i
    
    except Exception, e:
        print e.pgerror
        conn.close()
        sys.exit(1)
    
    conn.close()

''' 
This function takes care of all the initial db setup necessary for
the rest of the functions to work. This must be called before any other
function is called.
'''
def setup(db):
    if len(student_id_map) == 0:
        setStudentMap(db)
    

'''
Returns an array of the number of questions asked by every student
'''
def getNumQuestionsAsked(db=database):
    global student_id_map    
    try: 
        conn = psycopg2.connect(database=db, user='postgres')
        cur = conn.cursor()
        query = "SELECT anon_uid, post_params FROM monitored_actions " + \
        "WHERE post_params != '[]' AND url_path ~ '/questions/ask'"
        
        # Dictionary from anon_uid => list of question titles asked
        mon_questions = {}
        
        cur.execute(query)
        for rec in cur:
            uid, params = rec
            for key, val in eval(params):
                if key == 'title':
                    if uid not in mon_questions:
                        mon_questions[uid] = set([val[0]])
                    else:
                        mon_questions[uid].add(val[0])
        
        to_ret = [0]*len(student_id_map)
        for anon_uid, questions in mon_questions.iteritems():
            to_ret[ student_id_map[anon_uid] ] =  len(questions)
            
        return to_ret
                    
                
    except psycopg2.DatabaseError, e:
        print e.pgerror
        conn.close()
        sys.exit(1)
    
    conn.close()
       

#def getAllFeatures(): 
