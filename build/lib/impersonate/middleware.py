from django.conf import settings
from impersonate.helpers import check_allow_for_user, check_allow_for_uri


class ImpersonateMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and \
           '_impersonate' in request.session:
            new_user = request.session['_impersonate']
            if check_allow_for_user(request, new_user) and \
               check_allow_for_uri(request.path):
                request.user = new_user
                request.user.is_impersonate = True
