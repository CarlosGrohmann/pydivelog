from .divelogparser import Divelog
from .divelogpdf import DivelogPdf, DivelogVerifyPdf
import configparser
import sys
import os
import subprocess
from contextlib import suppress
from . divecmd_parser import readdata
import yaml
import logging


def load_config():
    config = configparser.ConfigParser()
    defaults = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','config','divelog')
    configfilepath = os.path.expanduser('~/.divelog')
    config.read([defaults, configfilepath])
    if not os.path.isfile(configfilepath):
        logging.debug('Create config file %', filepath)
        with open(filepath, 'w+') as f:
            config.write(f)
    return config

def get_args(args):
    import argparse
    parser = argparse.ArgumentParser(prog = 'pydivelog', description='Divelog handler V0.1.0')
    parser.add_argument('action', choices=['pdf', 'import', 'pdfverify'], help='Action to perform')
    parser.add_argument('--device', help='Device to read from')
    parser.add_argument('--file', help='File to import instead of reading device')
    parser.add_argument('--count', type=int, help='Number of sign fields')
    parser.add_argument('--startid', type=int, help='Startid of sign fields')
    parser.add_argument('-v', '--verbose', default=0, action='count', help='verbosity')
    return parser.parse_args(args)

def configure_logging(level):
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    loglevel = levels[min(len(levels)-1,level)]  # capped to number of levels
    logging.basicConfig(level=loglevel, format="%(asctime)s [%(levelname)-10s] | %(message)s")

args = get_args(sys.argv[1:])
configure_logging(args.verbose)
logger = logging.getLogger('pydivelog')
config = load_config()


def action_pdf():
    url = config['output']['baseurl']
    logging.debug('Divelog for url: %s', url)
    f = DivelogPdf(baseurl=url, tempdir=os.path.expanduser(config['output']['tempdir']))
    for i, e in enumerate(Divelog(os.path.expanduser(config['divelog']['path'])), 1):
        logging.debug('Add Dive to pdf: %d - %s', i, e)
        f.add_dive(i, verify=e.verify, **e.as_dict())

    name = os.path.join(os.path.expanduser(config['output']['dir']), config['output'].get('name', 'output.pdf'))
    logging.info('Writing PDF output %s', name)
    f.save(name)

def action_pdfverify():
    f = DivelogVerifyPdf(baseurl=config['output']['baseurl'], tempdir=os.path.expanduser(config['output']['tempdir']), startid=args.startid, count=args.count)
    name = os.path.join(os.path.expanduser(config['output']['dir']), 'verify.pdf')
    f.save(name)

def action_import():
    if not args.file:
        divecmd = os.path.expanduser(config['divecmd']['path'])
        with subprocess.Popen([divecmd, *config['divecmd']['args'].split(' ')], stdout=subprocess.PIPE) as proc:
            data = proc.stdout.read()
    else:
        data = open(args.file, 'r').read()
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

locals()['action_{0}'.format(args.action)]()

