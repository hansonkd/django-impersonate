from django.conf import settings
from impersonate.helpers import check_allow_for_user, check_allow_for_uri
from django.shortcuts import get_object_or_404


class ImpersonateMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and \
                '_impersonate' in request.session:
            model_str = getattr(settings, 'IMPERSONATE_USER_MODEL',
                                'django.contrib.auth.models.User')
            module, model = model_str.rsplit('.', 1)
            module = __import__(module, fromlist=[model])
            Model = getattr(module, model)
            pk = request.session['_impersonate']
            new_user = get_object_or_404(Model, pk=pk)
            if check_allow_for_user(request, new_user) and \
               check_allow_for_uri(request.path):
                request.user = new_user
                request.user.is_impersonate = True
