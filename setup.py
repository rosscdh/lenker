from distutils.core import setup
from setuptools import find_packages

setup(
    name='lenker',
    version='0.1',
    author="Ross Crawford-d'Heureuse",
    author_email='sendrossemail@gmail.com',
    packages=['lenker'],
    include_package_data=True,
    url='https://github.com/rosscdh/lenker',
    description='Extended integration of pybars for server-side Handlebars templates',
    long_description=open('README.md').read(),
    zip_safe=False,
    install_requires=[
        'pybars'
     ]
)