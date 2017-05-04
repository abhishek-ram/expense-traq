from django.utils import six
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib import messages


def user_in_groups(group, login_url=None, raise_exception=True):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """
    def check_groups(user):
        if isinstance(group, six.string_types):
            groups = (group, )
        else:
            groups = group
        # First check if the user has the permission (even anon users)
        user_groups = {g.name for g in user.groups.all()}
        if user_groups.intersection(set(groups)):
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False

    return user_passes_test(check_groups, login_url=login_url)


class DeleteMessageMixin(object):
    """
    Adds a success message on successful form submission.
    """
    success_message = ''

    def delete(self, request, *args, **kwargs):
        success_message = self.get_success_message(self.get_object())
        response = super(DeleteMessageMixin, self).delete(request)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, obj):
        return self.success_message % obj.__dict__

