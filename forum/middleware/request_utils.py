import forum

from forum.settings import MAINTAINANCE_MODE, APP_URL, APP_LOGO, APP_TITLE

from forum.http_responses import HttpResponseServiceUnavailable
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from forum.models import User
import logging

class RequestUtils(object):
    def process_request(self, request):
        # If not consented, only allow consent, logout
        if not request.user.is_authenticated() and not request.path.startswith('/account/'):
            return HttpResponseRedirect(reverse('auth_provider_signin', args=['edx']))
        if request.user.is_authenticated() and not 'test.' in APP_URL and (not any(map(lambda x: request.path.startswith(x), ['/logout/', '/account/'])) or request.path == '/account/signin/'):
            # Redirect to server for correct experimental group based on SHA512 hash of username, if necessary
            import hashlib
            hasher = hashlib.sha256()
            hasher.update(request.user.username)
            group = 'a' if ord(hasher.digest()[-1]) % 2 == 0 else 'b'
            if '-' + group + '.' not in APP_URL:
                # Generate a nonce and insert it into database of the new server,
                # then pass it in the URL to avoid double log-in
                import random, string
                # TODO: Use cryptographically-secure RNG
                nonce = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(64))
                try:
                    user = User.objects.using(group).get(username=request.user.username)
                    user.redirect_nonce = nonce
                    user.save(using=group)
                except User.DoesNotExist:
                    # Clone current user
                    user = request.user
                    user.redirect_nonce = nonce
                    save_id = user.id
                    user.id = None
                    user.save(using=group, force_insert=True)
                    user.id = save_id
                    
                return HttpResponseRedirect('http://cs1692x-' + group + '.moocforums.org/account/edx/done/?validate_email=yes&nonce=' + nonce)
        # On correct server now, force consent form on first visit, but still allow logout
        if request.user.is_authenticated() and not request.user.completed_consent and not any(map(lambda x: request.path.startswith(x), ['/consent/', '/logout/', '/account/'])):
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

