# coding=utf-8
"""
Pinyto cloud - A secure cloud database for your personal data
Copyright (C) 2019 Pina Merkert <pina@pinae.net>

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

from pymongo import MongoClient
from django.conf import settings


class MongoConnection:
    @staticmethod
    def create_mongo_client():
        if 'USER' in settings.MONGO_DB and 'PASSWORD' in settings.MONGO_DB:
            return MongoClient(settings.MONGO_DB['HOST'],
                               username=settings.MONGO_DB['USER'],
                               password=settings.MONGO_DB['PASSWORD'],
                               port=int(settings.MONGO_DB['PORT']))
        else:
            return MongoClient(settings.MONGO_DB['HOST'] if 'HOST' in settings.MONGO_DB else 'localhost',
                               port=int(settings.MONGO_DB['PORT']) if 'PORT' in settings.MONGO_DB else 27017)

    @staticmethod
    def get_db():
        return MongoConnection.create_mongo_client()[settings.MONGO_DB['NAME']
                                                     if 'NAME' in settings.MONGO_DB else 'pinyto']
