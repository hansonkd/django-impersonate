import re
from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage
from django.utils.safestring import mark_safe


def get_redir_path(request=None):
    next = None
    redirect_field_name = getattr(settings,
                                  'IMPERSONATE_REDIRECT_FIELD_NAME', None)
    if request and redirect_field_name:
        next = request.GET.get(redirect_field_name, None)
    return next or getattr(
        settings,
        'IMPERSONATE_REDIRECT_URL',
        getattr(settings, 'LOGIN_REDIRECT_URL', '/'),
    )


def get_redir_arg(request):
    redirect_field_name = getattr(settings,
                                  'IMPERSONATE_REDIRECT_FIELD_NAME', None)
    if redirect_field_name:
        next = request.GET.get(redirect_field_name, None)
        if next:
            return '?%s=%s' % (redirect_field_name, next)
    return ''


def get_redir_field(request):
    redirect_field_name = getattr(settings,
                                  'IMPERSONATE_REDIRECT_FIELD_NAME', None)
    if redirect_field_name:
        next = request.GET.get(redirect_field_name, None)
        if next:
            return mark_safe('<input type="hidden" name="%s" value="%s"/>' %
                             (redirect_field_name, next))
    return ''


def get_paginator(request, qs):
    try:
        page_number = int(request.GET.get('page', 1))
    except ValueError:
        page_number = 1

    paginator = Paginator(
        qs,
        int(getattr(settings, 'IMPERSONATE_PAGINATE_COUNT', 20)),
    )
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = None

    return (paginator, page, page_number)


def check_allow_staff():
    return (not getattr(settings, 'IMPERSONATE_REQUIRE_SUPERUSER', False))


def users_impersonable(request):
    ''' Returns a QuerySet of users that this user can impersonate.
        Uses the IMPERSONATE_CUSTOM_USER_QUERYSET if set, else, it
        returns all users
    '''
    if hasattr(settings, 'IMPERSONATE_CUSTOM_USER_QUERYSET'):
        custom_queryset_func = import_func_from_string(
            settings.IMPERSONATE_CUSTOM_USER_QUERYSET
        )
        return custom_queryset_func(request)
    else:
        return User.objects.all()


def check_allow_for_user(request, end_user):
    ''' Return True if some request can impersonate end_user
    '''
    if check_allow_impersonate(request):
        # start user can impersonate
        # Can impersonate anyone who's not a superuser and who is in your
        # queryset of 'who i can impersonate'
        upk = end_user.pk
        return (
            not end_user.is_superuser and
            users_impersonable(request).filter(pk=upk).count()
        )

    # start user not allowed impersonate at all
    return False


def import_func_from_string(string_name):
    ''' Given a string like 'mod.mod2.funcname' which refers to a function,
        return that function so it can be called
    '''
    mod_name, func_name = string_name.rsplit('.', 1)

    # from http://docs.python.org/faq/programming.html?highlight=importlib#import-x-y-z-returns-module-x-how-do-i-get-z
    mod = __import__(mod_name)
    for i in mod_name.split('.')[1:]:
        mod = getattr(mod, i)

    return getattr(mod, func_name)


def check_allow_impersonate(request):
    ''' Returns True if this request is allowed to do any impersonation.
        Uses the IMPERSONATE_CUSTOM_ALLOW function if required, else
        looks at superuser/staff status and IMPERSONATE_REQUIRE_SUPERUSER
    '''
    if hasattr(settings, 'IMPERSONATE_CUSTOM_ALLOW'):
        custom_allow_func = \
            import_func_from_string(settings.IMPERSONATE_CUSTOM_ALLOW)

        return custom_allow_func(request)
    else:
        # default allow checking:
        if not request.user.is_superuser:
            if not request.user.is_staff or not check_allow_staff():
                return False

        return True


def check_allow_for_uri(uri):
    uri = uri.lstrip('/')

    exclusions = getattr(settings, 'IMPERSONATE_URI_EXCLUSIONS', (r'^admin/',))
    if not isinstance(exclusions, (list, tuple)):
        exclusions = (exclusions,)

    for exclusion in exclusions:
        if re.search(exclusion, uri):
            return False

    return True
