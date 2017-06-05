import yaml

class DivelogData(object):

    def __init__(self, value):
        if isinstance(value, dict):
            self._value = {k: DivelogDataFactory.create(k, v) for k,v in
                         value.items()}
        else:
            self._value = value

    def keys(self):
        if isinstance(self._value, dict):
            return self._value.keys()
        else:
            return []

    def __getitem__(self, key):
        return self._value[key]

    def __repr__(self):
        return str(self)

    def __str__(self):
        if isinstance(self._value, list):
            return ', '.join(map(str, self._value))
        return str(self._value)

    def append(self, value):
        self._value.append(value)

class DiveSuit(DivelogData):
    def __str__(self):
        extra = ''
        for key, val in self._value.items():
            if key != 'type':
                extra += str(val)
        extra = ' ({0})'.format(extra) if len(extra) else ''
        return '{type}{extra}'.format(type=self['type'], extra=extra)

class DiveUnit(DivelogData):
    def __init__(self, unit, value):
        super().__init__(value)
        self._unit = unit or self.unit
    def __str__(self, unit=None):
        if isinstance(self._value, str):
            return self._value
        else:
            return '{type} {unit}'.format(type=self._value, unit=self._unit)

class DiveDate(DivelogData):
    def __str__(self, unit=None):
        return datetime.strptime(self.value, "%d/%m/%y %H:%M")

class DiveComputerData(DivelogData):
    def __str__(self):
        extra = ''
        for key, val in self._value.items():
            if key != 'type':
                extra += str(val)
        extra = ' ({0})'.format(extra) if len(extra) else ''
        return '{type}{extra}'.format(type=self['type'], extra=extra)

class DivelogDataFactory():

    __slots__ = []
    specialized_types = { 'divesuit': DiveSuit,
                         'thickness': lambda x: DiveUnit('mm', x),
                         'lead': lambda x: DiveUnit('kg', x),
                         'duration': lambda x: DiveUnit('min', x),
                         'maxdepth': lambda x: DiveUnit('m', x),
                         'sight': lambda x: DiveUnit('m', x),
                         'watertemperature': lambda x: DiveUnit('°C', x),
                         'airtemperature': lambda x: DiveUnit('°C', x),
                         'pressure_start': lambda x: DiveUnit('bar', x),
                         'pressure_end': lambda x: DiveUnit('bar', x),
                         'tank': lambda x: DiveUnit('l', x),
                         'data': DiveComputerData
                         }

    @classmethod
    def create(cls, key, value):
        try:
            return cls.specialized_types[key](value)
        except:
            return DivelogData(value)

class DivelogFile(DivelogData):

    def __init__(self, filename):
        with open(filename, 'r') as f:
            super().__init__(yaml.load(f.read()))


class ListFile(DivelogFile):

    def __init__(self, typ, filename):
        super().__init__(filename)
        for name, elem in self._value.items():
            self._value[name] = typ(name, **elem)

        self._alias = {x: key for key, elem in self._value.items() if 'alias'
                       in elem for x in elem['alias']}

    def __getitem__(self, key):
        if not isinstance(key, str):
            key = str(key)
        if not key in self._value:
            key = self._alias[key]
        return self._value[key]

    def __len__(self):
        return len(self._value)

    def __contains__(self, key):
        return key in self._value or key in self._alias


class ListElement(object):

    def __init__(self, **kwargs):
        self._info = kwargs

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        return self._info[key]

    def __contains__(self, key):
        return key in self._info or hasattr(self, key)

    def __str__(self):
        return '{name}'.format(name=self.name)

    def __repr__(self):
        return self.__str__()


class Location(ListElement):

    def __init__(self, name: str, coordinates: dict, water: str, watersname: str,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        if not 'alias' in self._info:
            self._info['alias'] = []
        self._info['alias'].append(name)
        self.coordinates = (coordinates['latitude'], coordinates['longitude'])
        self.water = water
        self.watersname = watersname


class LocationList(ListFile):

    def __init__(self, filename):
        super().__init__(Location, filename)


class Person(ListElement):

    def __init__(self, name: str, fullname: str = None, **kwargs):
        super().__init__(**kwargs)
        self.name = fullname or name


class PersonList(ListFile):

    def __init__(self, filename):
        super().__init__(Person, filename)

