"""A yaml file based divelog

"""

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'pydivelog',
    version = '0.1.0',
    description = 'A yaml file based divelog.',
    long_description = long_description,
    url = 'https://github.com/m42e/pydivelog',
    download_url = 'https://github.com/m42e/pydivelog/archive/v0.1.0.tar.gz',
    author = 'Matthias Bilger',
    author_email = 'matthias@bilger.info',
    license = 'MIT',
    classifiers=[
        'Topic :: Text Processing',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    keywords = 'dive divelog pdf',
    packages = ['pydivelog', 'pydivelog.divelogparser', 'pydivelog.divelogpdf'],
    package_data={'pydivelog':['config/divelog', 'templates/*', 'templates/**/*']},
    install_requires = ['yafte'],
)
