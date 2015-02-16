# coding=utf-8
"""
Pinyto cloud - A secure cloud database for your personal data
Copyright (C) 2105 Johannes Merkert <jonny@pinyto.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
        check_for_jobs(None)