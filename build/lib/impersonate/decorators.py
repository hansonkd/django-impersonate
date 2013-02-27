from django.conf import settings
from django.shortcuts import redirect
from django.utils.http import urlquote
from django.contrib.auth import REDIRECT_FIELD_NAME
from impersonate.helpers import get_redir_path, check_allow_impersonate


def allowed_user_required(view_func):
    def _checkuser(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return redirect('%s?%s=%s' % (
                settings.LOGIN_URL,
                REDIRECT_FIELD_NAME,
                urlquote(request.get_full_path()),
            ))

        if getattr(request.user, 'is_impersonate', False):
            # Do not allow an impersonated session to use the 
            # impersonate views.
            return redirect(get_redir_path())

        if check_allow_impersonate(request):
            # user is allowed to impersonate
            return view_func(request, *args, **kwargs)
        else:
            # user not allowed impersonate at all
            return redirect(get_redir_path())

    return _checkuser
