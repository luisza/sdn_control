from setuptools import setup, find_packages
import os

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
	'Topic :: Software Development :: Libraries :: Python Modules',
	'Development Status :: 4 - Beta',
]

README = """Sdn control ryu apps"""

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))



setup(
    author='Luis Zarate',
    author_email='luis.zarate@solvosoft.com',
    name='sdnctlryuapps',
    version='0.0.1',
    description='Sdn ryu apps DHCP, and DPInfo',
    long_description=README,
    url='https://github.com/luisza/sdn_control/',
    license='GNU General Public License v3 (GPLv3)',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'setuptools',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False
)
