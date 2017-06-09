import xml.etree.ElementTree as ET
import os
import sys
from collections import defaultdict, namedtuple
from pprint import pprint
import yaml

class DiveSample(object):
    def __init__(self, time):
        self.time = time
        self.tankpressure = Pressure(None, None)
        self.vendor = Vendordata(None, None)
        self.decompression = Decompression(None, None, None)

Pressure = namedtuple('Pressure', ['tank', 'value'])
Vendordata = namedtuple('Vendordata', ['type', 'data'])
Decompression = namedtuple('Decompression', ['type', 'depth', 'duration'])

class Dive(object):
    def __init__(self, date, time):
        self.date = date
        self.time = time
        self._samples = []

    def append(self, sample: DiveSample):
        self._samples.append(sample)

    def __len__(self):
        return len(self._samples)

    def __getitem__(self, key):
        return self._samples[key]

    @property
    def name(self):
        return '{}-{}.yaml'.format(self.date, ''.join(self.time.split(':')[0:2]))

    @property
    def dir(self):
        return os.path.join(*self.date.split('-'))

    def gp(self):
        data = []
        ltemp = ''
        for s in sorted(self._samples, key=lambda x:int(x.time)):
            if hasattr(s, 'temp'):
                ltemp = s.temp
            data.append('{0}\t-{1}\t{2} '.format(float(s.time)/60.0, s.depth, ltemp))

        text = '\n'.join(data)
        return text

    def yaml(self):
        data = []
        mintemp = 9999
        lasttemp = ''
        for s in sorted(self._samples, key=lambda x:int(x.time)):
            if hasattr(s, 'temp'):
                mintemp = min(mintemp, float(s.temp))
                lasttemp = float(s.temp)
            data.append({
                'time': float(s.time)/60.0,
                'depth': float(s.depth),
                'temp': lasttemp,
                'vendor': dict(s.vendor._asdict()),
                'pressure': dict(s.tankpressure._asdict()),
                'deco': dict(s.decompression._asdict()),
            })

        return {
            'duration': int(int(self.duration)/60),
            'maxdepth': self.depth,
            'fingerprint': self.fingerprint,
            'watertemperature': mintemp,
            'data': data,
        }



def gv(xml, element):
    return xml.find(element).attrib['value']

def readdata(data):
    root = ET.fromstring(data)
    dives = []
    for dive in root.iter('dive'):
        d = Dive(dive.attrib['date'], dive.attrib['time'])
        d.duration = dive.attrib['duration']
        d.fingerprint = dive.find('fingerprint').text
        d.gasmixes = []
        for gasmix in dive.iter('gasmix'):
            d.gasmixes.append(gasmix.attrib)
        d.depth = float(dive.find('depth').attrib['max'])
        for sample in dive.iter('sample'):
            s = DiveSample(sample.attrib['time'])
            s.depth = gv(sample,'depth')
            if float(s.depth) > 0.00:
                s.temp = gv(sample,'temp')
                s.tankpressure = Pressure(**sample.find('pressure').attrib)
                s.vendor = Vendordata(**sample.find('vendor').attrib)
                s.decompression = Decompression(**sample.find('deco').attrib)
            d.append(s)
        dives.append(d)
    return dives
