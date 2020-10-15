import os

from distutils.core import setup

name = 'nbsetuptools'

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))
pkg_root = pjoin(here, name)

packages = []
for d, _, _ in os.walk(pjoin(here, name)):
    if os.path.exists(pjoin(d, '__init__.py')):
        packages.append(d[len(here)+1:].replace(os.path.sep, '.'))

package_data = {'nbsetuptools.tests': [pjoin('support', '*')]}

setup(
    name=name,
    version='0.1.5',
    url="https://github.com/anaconda-server/nbsetuptools",
    author="Continuum Analytics",
    author_email="info@continuum.io",
    description="Help you install your nbextensions",
    packages=packages,
    package_data=package_data,
    license='BSD',
    install_requires=[
        'funcsigs',
        'notebook',
    ]
)
