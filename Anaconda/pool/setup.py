#!/usr/bin/env python

import setuptools
import repo_mirror


requirements = ['boto3', 'ruamel.yaml', 'jinja2']
test_requirements = ['pytest']


setuptools.setup(
    name='repo_mirror',
    version=repo_mirror.__version__,
    description='Anaconda utility to generate airgap tarball files',
    author='Dave Kludt',
    author_email='dkludt@anaconda.com',
    install_requires=requirements,
    extras_require={
        'tests': test_requirements
    },
    entry_points={
        'console_scripts': [
            'airgap=repo_mirror.airgap:main'
        ]
    },
    packages=setuptools.find_packages(),
    package_data={'repo_mirror': ['templates/*.yaml']},
    zip_safe=False
)
