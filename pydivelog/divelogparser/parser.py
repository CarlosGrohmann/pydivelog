import yaml
import glob
import os
import collections
from . objects import PersonList, LocationList
from . entry import Entry
import logging


class Files(object):

    def __init__(self, basepath):
        self.basepath = basepath

    @property
    def locationfile(self):
        return '{0}/meta/locations.yaml'.format(self.basepath)

    @property
    def personfile(self):
        return '{0}/meta/persons.yaml'.format(self.basepath)

    @property
    def entries(self):
        pathpattern = '{0}/[1-2][0-9][0-9][0-9]/**/*.yaml'.format(self.basepath)
        return glob.iglob(pathpattern, recursive=True)


class Divelog(object):
    '''represent a complete divelog'''

    def __init__(self, basepath):
        self.logger = logging.getLogger(__name__)
        self.basepath = os.path.expanduser(basepath)
        self.logger.info('Using divelog at %s', self.basepath)
        self.files = Files(basepath)
        self.update()

    def update(self):

        self.logger.debug('Reading locations at %s', self.files.locationfile)
        self.locations = LocationList(self.files.locationfile)
        self.logger.debug('Reading person at %s', self.files.personfile)
        self.persons = PersonList(self.files.personfile)
        fileentries = {}
        self.logger.debug('Reading dives')
        for filename in self.files.entries:
            self.logger.debug('Dive %s', filename)
            entry = Entry(filename, self.locations, self.persons)
            fileentries[str(entry['date'])] = entry
        self.logger.debug('Sorting dives')
        self.entries = collections.OrderedDict(sorted(fileentries.items()))

    def __iter__(self):
        return self.entries.values().__iter__()

    def __getitem__(self, key):
        return self.entries[key]

    def __contains__(self, key):
        return key in self.entries

    def __len__(self):
        return len(self.entries)
