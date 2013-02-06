import os
import sys
this_dir = os.path.dirname(os.path.realpath(__file__))
srv_osqa_root = os.path.dirname(this_dir)
subdomain = os.path.basename(this_dir)
sys.path.append(srv_osqa_root)
sys.path.append(srv_osqa_root + '/' + subdomain)
# The first part of this module name should be identical to the directory name
# of the OSQA source.  For instance, if the full path to OSQA is
# /home/osqa/osqa-server, then the DJANGO_SETTINGS_MODULE should have a value
# of 'osqa-server.settings'.
os.environ['DJANGO_SETTINGS_MODULE'] = subdomain + '.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
