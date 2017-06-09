from .divelogparser import Divelog
from .divelogpdf import DivelogPdf, DivelogVerifyPdf
import configparser
import sys
import os
import subprocess
from contextlib import suppress
from . divecmd_parser import readdata
import yaml


def load_config():
    config = configparser.ConfigParser()
    defaults = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','config','divelog')
    configfilepath = os.path.expanduser('~/.divelog')
    config.read([defaults, configfilepath])
    if not os.path.isfile(configfilepath):
        with open(filepath, 'w+') as f:
            config.write(f)
    return config

def get_params(args):
    import argparse
    parser = argparse.ArgumentParser(prog = 'pydivelog', description='Divelog handler V0.1.0')
    parser.add_argument('action', choices=['pdf', 'import', 'pdfverify'], help='Action to perform')
    parser.add_argument('--device', help='Device to read from')
    parser.add_argument('--file', help='File to import instead of reading device')
    parser.add_argument('--count', type=int, help='Number of sign fields')
    parser.add_argument('--startid', type=int, help='Startid of sign fields')
    return parser.parse_args(args)

config = load_config()
params = get_params(sys.argv[1:])

def action_pdf():
    f = DivelogPdf(baseurl=config['output']['baseurl'], tempdir=os.path.expanduser(config['output']['tempdir']))
    for i, e in enumerate(Divelog(os.path.expanduser(config['divelog']['path'])), 1):
        f.add_dive(i, verify=e.verify, **e.as_dict())

    f.save('output.pdf')

def action_pdfverify():
    f = DivelogVerifyPdf(baseurl=config['output']['baseurl'], tempdir=os.path.expanduser(config['output']['tempdir']), startid=params.startid, count=params.count)
    f.save('verify.pdf')

def action_import():
    if not params.file:
        divecmd = os.path.expanduser(config['tools']['divecmd'])
        with subprocess.Popen([divecmd, *config['divecmd']['params'].split(' ')], stdout=subprocess.PIPE) as proc:
            data = proc.stdout.read()
    else:
        data = open(params.file, 'r').read()
    for dive in readdata(data):
        filename = os.path.join(os.path.expanduser(config['divelog']['path']), dive.dir, dive.name)
        print(filename)
        if os.path.isfile(filename):
            print('file exists')
        else:
            with suppress(FileExistsError):
                path = os.path.dirname(filename)
                os.makedirs(path)
            with open(filename, 'w+') as f:
                f.write(yaml.dump(dive.yaml()))





locals()['action_{0}'.format(params.action)]()

