# coding=utf-8
"""
This File is part of Pinyto
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    This class runs periodic jobs for all users.
    """
    args = '<none>'
    help = 'Completes the data for all PinytoAPI classes'

    def handle(self, *args, **options):
        """
        This command runs periodic jobs for all users.
        @param args:
        @param options:
        @return: bool
        """
        pass  # TODO: Implement this.
