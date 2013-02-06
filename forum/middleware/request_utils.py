import forum

from forum.settings import MAINTAINANCE_MODE, APP_LOGO, APP_TITLE

from forum.http_responses import HttpResponseServiceUnavailable
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

class RequestUtils(object):
    def process_request(self, request):
        # If not consented, only allow consent, logout
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

