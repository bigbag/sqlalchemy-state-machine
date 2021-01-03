#!/usr/bin/env python
from pp_common.version import __version__
from setuptools import find_packages, setup


def get_requirements(extra_name):
    requirements_path = f"requirements/{extra_name}.txt"
    with open(requirements_path, "r") as f:
        return [x.strip() for x in f.readlines()]


CLASSIFIERS = [
    "Development Status :: 3 - Beta",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.8",
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
    version=__version__,
    url="https://github.com/bigbag/sqlalchemy-state-machine",
    platforms=CLASSIFIERS,
    install_requires=get_requirements("prod"),
    extras_require={"tests": get_requirements("tests"), "linters": get_requirements("linters")},
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="",
)
