from distutils.core import setup
from setuptools import find_packages
setup(
    name='eth_log',
    packages=find_packages(),
    version='0.2.0',
    description="Eth-log - python tools to collect and process ethereum smart contracts' event logs ",
    author='Ramtin Seraj',
    author_email='mehdizadeh.ramtin@gmail.com',
    url='https://github.com/ramtinms/ethereum-log',
    download_url='https://github.com/ramtinms/ethereum-log/tarball/0.1',
    keywords=['ethereum', 'blockchain', 'smart contract', 'eth', 'event log'],
    classifiers=['Intended Audience :: Information Technology',
                 'Intended Audience :: Science/Research',
                 'Topic :: Scientific/Engineering',
                 'Topic :: Scientific/Engineering :: Information Analysis',
                 ],
    install_requires=[
        "requests",
        "pysha3",
        "pandas",
    ],

)
