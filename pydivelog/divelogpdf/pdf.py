from yafte import YaFTe
import pyqrcode
import tempfile
import uuid
import hashlib
import os
import subprocess


class DivelogPdf(object):
    def __init__(self, template=None, baseurl=None, tempdir=None):
        p= os.path
        path = p.join(p.dirname(p.realpath(__file__)),'..', 'templates','divelog_template.yaml')
        self._template = YaFTe(template or path)
        self._temp = tempdir or '/tmp'
        self._baseurl = baseurl

    def _create_qrcode(self, content):
        fid = hashlib.sha1(content.encode('utf8')).hexdigest()
        filename = os.path.join(self._temp, fid +'.png')
        if not os.path.isfile(filename):
            url = pyqrcode.create(content, error='L')
            url.png(filename, scale=6, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xff], quiet_zone=1)
        return filename

    def _setup_gnuplot(self,filename):
        setup = '''
# data file
set encoding utf8
set term pngcairo size 1532,600 enhanced font 'Verdana'
set grid front
set xlabel "min"
set y2range [0 : 40]
set y2tics
set yrange [-40: 0]
set key bottom right
set ylabel "m" rotate by 0
set y2label "°C" rotate by 0
set samples 150
        '''
        with open('{0}.gp'.format(filename), 'w+') as f:
            f.write(setup)
        pass

    def _create_graph(self, data):
        fid = hashlib.sha1(str(data).encode('utf8')).hexdigest()
        filename = os.path.join(self._temp, fid)
        pngfile = '{}.png'.format(filename)
        if os.path.isfile(pngfile):
            return pngfile
        self._setup_gnuplot(filename)
        graph = '''
# data file
file="{0}.data"
stats file using 1:2 prefix "depth" nooutput
set output "{0}.png"
set xrange [0: depth_max_x]
# Mark the max depth
set label 1 at depth_pos_min_y, depth_min_y-2 sprintf('%.1f m',depth_min_y) center offset 4,0.5 front
set arrow 1 from depth_pos_min_y, depth_min_y-2 to depth_pos_min_y, depth_min_y fill front
plot file using 1:2 smooth csplines with filledcurve x1 title "" axes x1y1 lt rgb '#cccccc', \\
        '' using 1:2 smooth csplines with l lt rgb '#000000' title "Tiefe", \\
		depth_min_y axes x1y1 title "Max. Tiefe" lw 3 lt rgb '#ffA500', \\
		file using 1:3 smooth csplines with line title "Temperatur" axes x1y2 lt rgb '#cc0000' lw 2
        '''
        with open('{0}.gp'.format(filename), 'a+') as f:
            f.write(graph.format(filename))
        with open('{}.data'.format(filename), 'w+') as f:
            f.write('0 0 {}\n'.format(data[0]['temp']))
            for s in data:
                f.write('{time} -{depth} {temp}\n'.format(**s))
            f.write('{0} 0 {1}\n'.format(data[-1]['time']+data[0]['time'], data[-1]['temp']))
        subprocess.check_call('gnuplot', stdin=open('{0}.gp'.format(filename)))

        return pngfile

    def add_dive(self, id, verify=None, **kwargs):
        pagedata = {}
        pagedata.update(kwargs.items())
        pagedata['id'] = id
        if (self._baseurl):
            pagedata['qrcode_id'] = self._create_qrcode(self._baseurl + str(id))
            if verify:
                pagedata['qrcode_verify'] = self._create_qrcode(self._baseurl + str(id)+'/v/'+verify)
        if 'data' in pagedata:
            pagedata['graph'] = self._create_graph(pagedata['data'])
        self._template.add_page(**pagedata)

    def save(self, filename):
        self._template.output(filename)


class DivelogVerifyPdf(DivelogPdf):
    def __init__(self, template=None, baseurl=None, tempdir=None, startid=None, count=None):
        p= os.path
        path = p.join(p.dirname(p.realpath(__file__)),'..', 'templates','verify_template.yaml')
        super().__init__(template or path, baseurl, tempdir)
        count = count or 3

        for pages in range(int(count/3)):
            data = {}
            if startid is not None:
                data['qrcode_id'] = self._create_qrcode(self._baseurl + str(startid))
                data['qrcode_id2'] = self._create_qrcode(self._baseurl + str(startid+1))
                data['qrcode_id3'] = self._create_qrcode(self._baseurl + str(startid+2))
                data['id'] = str(startid)
                data['id2'] = str(startid+1)
                data['id3'] = str(startid+2)
                startid += 3
            self._template.add_page(**data)

    def save(self, filename):
        self._template.output(filename)
