import re
import os
import datetime
import hashlib
from . objects import DivelogFile, LocationList, PersonList, DivelogData


class Entry(DivelogFile):
    __slots__ = ['data', 'filename', 'date']
    dateregex = re.compile(
        '''(?P<year>[1-2][0-9]{3})-           # year
           (?P<month>(?:0[0-9])|(?:1[0-2]))-  # month
           (?P<day>(?:[012][0-9])|(?:3[01]))- # day
           (?P<hour>(?:[01][0-9])|(?:2[0-3])) # hour
           (?P<minute>(?:[0-5][0-9]))         # minute''',
        flags=re.VERBOSE)

    def __init__(self, filename, locations: LocationList, buddies: PersonList):
        super().__init__(filename)
        self.filename = filename
        self._setdate(filename)
        self._value['location'] = locations[self._value['location']]
        self._value['water'] = self._value['location']['water']
        self._value['watersname'] = self._value['location']['watersname']
        cur_buddies = []
        if 'buddies' in self._value:
            for buddy in self._value['buddies']:
                cur_buddies.append(buddies[buddy])
            self._value['buddies'] = DivelogData(cur_buddies)


    def _setdate(self, filename):
        key = os.path.splitext(os.path.basename(filename))[0]
        m = self.dateregex.match(key)
        date = {k: int(v) for k, v in m.groupdict().items()}
        self._value['date'] = datetime.datetime(**date)

    def __str__(self):
        return '{date} {loc}'.format(date=self._value['date'],
                                     loc=self._value['location'])

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return self.date < other.date

    def as_dict(self):
        return self._value

    @property
    def verify(self):
        hstring = '{date}{location}'.format(**self._value)
        print(hstring)
        return hashlib.sha1(hstring.encode('utf8')).hexdigest()[0:8]
