from __future__ import division, print_function, unicode_literals

from django.contrib.auth.models import User, Group


def create_user(username, mail="a@bc.de", password=None,
                groups=()):
    if password:
        new_user = User.objects.create_user(username, mail, password)
    else:
        new_user = User(username=username, email=mail)
        new_user.save()
    for group in groups:
        Group.objects.get(name=group).user_set.add(new_user)

    return new_user