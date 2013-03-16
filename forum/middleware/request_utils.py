import forum
import os

from urllib import urlencode
from forum.settings import MAINTAINANCE_MODE, APP_URL, APP_LOGO, APP_TITLE

from forum.http_responses import HttpResponseServiceUnavailable
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from forum.models import User
import logging
import re

def get_subdomain():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    return os.path.basename(root_dir)

def transfer(user, group, path):
    # Generate a nonce and insert it into database of the new server,
    # then pass it in the URL to avoid double log-in
    import random, string
    # TODO: Use cryptographically-secure RNG
    nonce = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(64))
    try:
        user = User.objects.using(group).get(username=user.username)
        user.redirect_nonce = nonce
        user.save(using=group)
    except User.DoesNotExist:
        # Clone current user
        user = user
        user.redirect_nonce = nonce
        save_id = user.id
        user.id = None
        user.save(using=group, force_insert=True)
        user.id = save_id

    subdomain = get_subdomain()
    return HttpResponseRedirect('http://' + subdomain + '-' + group + '.moocforums.org/account/edx/done/?' + urlencode({'validate_email': 'yes', 'nonce': nonce, 'path': path}))

def anonymize(uid):
    from AnonymizerClient import AnonymizerClient
    PORT_NUM = 5000
    client = AnonymizerClient(PORT_NUM)
    return client.anonymize(int(uid))

def is_user_identifiable(params_iter, user_ids):    
    for k, v_list in params_iter:
	for i in user_ids:
	    if i in k:
	        return True
	    for v in v_list:
	        if i in v:
		    return True
    return False

def monitor_activity(request):
    if not request.user:
        # This case should never be hit since we already check for authentication
	logging.error("For monitoring activity: Trying to track a user who is of object type NoneType")
	return

    user_ids = [request.user.username, request.user.first_name, request.user.last_name, request.user.email]
    user_ids = filter(lambda x: x != '' , user_ids)
    # A list of information that is identifiable to a person
    if (not is_user_identifiable(request.GET.iterlists(), user_ids)) and (not is_user_identifiable(request.POST.iterlists(), user_ids)):
    	from django.db import connection, transaction
    	cursor = connection.cursor()
    	info_to_monitor = [anonymize(request.user.id), request.path, request.method, str(request.GET.lists()), str(request.POST.lists()), str(request.COOKIES)]
    	sql_query = "INSERT INTO monitored_actions (anon_uid, url_path, http_method, get_params, post_params, cookies) VALUES (%s, %s, %s, %s, %s, %s)" 
    	cursor.execute(sql_query, info_to_monitor)
    	transaction.commit_unless_managed()


class RequestUtils(object):
    def process_request(self, request):
        full_path = request.REQUEST.get('path', request.path + ('?' if urlencode(request.GET) != '' else '') + urlencode(request.GET))

	# If not consented, only allow consent, logout
        if not request.user.is_authenticated() and not request.path.startswith('/account/'):
            return HttpResponseRedirect(reverse('auth_provider_signin', args=['edx']) + '?' + urlencode({'path': full_path}))
        
	# If an authenticated user is present, monitor his activity
	if request.user.is_authenticated():
	    monitor_activity(request)

	if request.user.is_authenticated() and not 'test.' in APP_URL and (not any(map(lambda x: request.path.startswith(x), ['/logout/', '/account/'])) or request.path == '/account/signin/' or re.match('/account/.*/signin/$', request.path)):
            # Redirect to server for correct experimental group based on SHA512 hash of username, if necessary
            import hashlib
            hasher = hashlib.sha256()
            hasher.update(request.user.username)
            group = 'a' if ord(hasher.digest()[-1]) % 2 == 0 else 'b'
            if '-' + group + '.' not in APP_URL and not request.user.is_superuser:
                return transfer(request.user, group, full_path)

        # On correct server now, force consent form on first visit, but still allow logout
        if request.user.is_authenticated() and not request.user.completed_consent and not any(map(lambda x: request.path.startswith(x), ['/consent/', '/logout/', '/account/'])) and not request.user.is_superuser:
            return HttpResponseRedirect(reverse('consent'))

        if MAINTAINANCE_MODE.value is not None and isinstance(MAINTAINANCE_MODE.value.get('allow_ips', None), list):
            ip = request.META['REMOTE_ADDR']

            if not ip in MAINTAINANCE_MODE.value['allow_ips']:
                return HttpResponseServiceUnavailable(MAINTAINANCE_MODE.value.get('message', ''))

        if request.session.get('redirect_POST_data', None):
            request.POST = request.session.pop('redirect_POST_data')
            request.META['REQUEST_METHOD'] = "POST"

        self.request = request
        forum.REQUEST_HOLDER.request = request
        return None

    def process_response(self, request, response):
        forum.REQUEST_HOLDER.request = None
        return response

