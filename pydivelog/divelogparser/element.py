class Entry(DivelogFile):
    __slots__ = ['data', 'filename', 'date']
    dateregex = re.compile(
        '''(?P<year>[1-2][0-9]{3})-           # year
           (?P<month>(?:0[0-9])|(?:1[0-2]))-  # month
           (?P<day>(?:[012][0-9])|(?:3[01]))- # day
           (?P<hour>(?:[01][0-9])|(?:2[0-3])) # hour
           (?P<minute>(?:[0-5][0-9]))         # minute''',
        flags=re.VERBOSE)

    def __init__(self, filename, locations: LocationList):
        super().__init__(filename)
        self.filename = filename
        self._setdate(filename)
        self.location = locations[self.data['location']]

    def _setdate(self, filename):
        key = os.path.splitext(os.path.basename(filename))[0]
        m = self.dateregex.match(key)
        date = {k: int(v) for k, v in m.groupdict().items()}
        self.date = datetime.datetime(**date)

    def __str__(self):
        return '{date} {loc}'.format(date=self.date, loc=self.location)

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return self.date < other.date
