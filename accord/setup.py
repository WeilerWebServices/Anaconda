#!/usr/bin/env python

import setuptools
import accord


requirements = ['sh', 'pyyaml']
test_requirements = ['mock', 'flake8', 'nose']


setuptools.setup(
    name='accord',
    version=accord.__version__,
    url='https://github.com/oldarmyc/accord',
    license='Apache License, Version 2.0',
    author='Dave Kludt',
    author_email='dkludt@anaconda.com',
    description=(
        'Backup and restore Anaconda Enterprise 5'
    ),
    zip_safe=False,
    platforms='any',
    install_requires=requirements,
    extras_require={
        'tests': test_requirements
    },
    entry_points={
        'console_scripts': [
            'accord=accord.process:main'
        ]
    },
    packages=['accord'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)
