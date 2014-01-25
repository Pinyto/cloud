# coding=utf-8
"""
This File is part of Pinyto
"""

from django.core.management.base import BaseCommand, CommandError
from api_prototype.views import ApiClasses


class Command(BaseCommand):
    """
    This class completes the data for all PinytoAPI classes.
    """
    args = '<none>'
    help = 'Completes the data for all PinytoAPI classes'

    def handle(self, *args, **options):
        """
        This command completes the data for all PinytoAPI classes.
        @param args:
        @param options:
        @return: bool
        """
        all_complete = True
        for api_class_origin, api_class_name in ApiClasses:
            module = __import__(api_class_origin, globals(), locals(), api_class_name)
            api_object = getattr(module, api_class_name)()
            if not api_object.complete():
                all_complete = False
                # raise CommandError('Completion in ' + api_class_name + 'failed.')

        #if all_complete:
        #    self.stdout.write('[Cron-Complete]: Successfully completed all data.')
        #else:
        #    self.stdout.write('[Cron-Complete]: ERROR: Could not complete all data.')
