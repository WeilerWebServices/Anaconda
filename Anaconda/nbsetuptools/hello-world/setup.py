import setuptools
from hello_world import _version


setuptools.setup(
    name="hello_world",
    version=_version.__version__,
    url="https://github.com/anaconda-server/anaconda-nb-extensions",
    author="Continuum Analytics",
    author_email="info@continuum.io",
    description="Example of a server extension for Jupyter notebook",
    long_description=open('README.md').read(),
    packages=setuptools.find_packages(),
)
