# coding=utf-8
"""
This File is part of Pinyto
"""

from django.core.management.base import BaseCommand
from api_prototype.views import check_for_jobs


class Command(BaseCommand):
    """
    This command tries to run all open jobs.
    """
    args = '<none>'
    help = 'Run all open jobs'

    def handle(self, *args, **options):
        """
        This command tries to run all open jobs.
        @param args:
        @param options:
        @return: bool
        """
        check_for_jobs()