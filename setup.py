#!/usr/bin/env python
from setuptools import find_packages, setup
from importlib.machinery import SourceFileLoader

version = SourceFileLoader("version", "sqlalchemy_state_machine/version.py").load_module()


CLASSIFIERS = [
    "Development Status :: 3 - Beta",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Operating System :: OS Independent",
    "Topic :: System :: Networking",
    "Topic :: Software Development",
    "Topic :: Software Development :: Libraries",
    "Environment :: Console",
    "Intended Audience :: Developers",
]

setup(
    author="Pavel Liashkov",
    author_email="pavel.liashkov@protonmail.com",
    name="sqlalchemy-state-machine",
    description="Helper for add transitions functionality in sqlalchemy",
    version=str(version.VERSION),
    url="https://github.com/bigbag/sqlalchemy-state-machine",
    platforms=CLASSIFIERS,
    install_requires=["SQLAlchemy==1.3.22", "transitions==0.8.6"],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="",
)
