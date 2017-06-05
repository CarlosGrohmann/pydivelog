from yafte import YaFTe
import pyqrcode
import tempfile
import uuid
import os

class DivelogPdf(object):
    def __init__(self, template=None, baseurl=None):
        p= os.path
        path = p.join(p.dirname(p.realpath(__file__)),'..', 'templates','divelog_template.yaml')
        self._template = YaFTe(template or path)
        self._baseurl = baseurl
        self._tempdir = tempfile.TemporaryDirectory()

    def _create_qrcode(self, content):
        filename = os.path.join(self._tempdir.name, str(uuid.uuid4())+'.png')
        url = pyqrcode.create(content, error='L')
        url.png(filename, scale=6, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xff], quiet_zone=1)
        return filename

    def add_dive(self, id, verify=None, **kwargs):
        pagedata = {}
        pagedata.update(kwargs.items())
        pagedata['id'] = id
        if (self._baseurl):
            pagedata['qrcode_id'] = self._create_qrcode(self._baseurl + str(id))
            if verify:
                pagedata['qrcode_verify'] = self._create_qrcode(self._baseurl + str(id)+'/v/'+verify)
        self._template.add_page(**pagedata)

    def save(self, filename):
        self._template.output(filename)


