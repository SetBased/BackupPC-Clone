from codecs import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='BackupPC-Clone',

    version='1.0.1',

    description='A tool for cloning the data of a BackupPC instance',
    long_description=long_description,

    url='https://github.com/SetBased/BackupPC-Clone',

    author='Set Based IT Consultancy',
    author_email='info@setbased.nl',

    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: System Administrators',
        'Topic :: System :: Archiving :: Backup',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='BackupPC, clone, copy',

    packages=find_packages(exclude=['build', 'test']),

    install_requires=['cleo==0.6.4'],

    entry_points={
        'console_scripts': [
            'backuppc-clone = backuppc_clone:main',
        ],
    },

    package_data={'': ['lib/ddl/*.sql']},
)
