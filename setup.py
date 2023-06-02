#!/usr/bin/env python

from os import path
from setuptools import setup, find_packages

root = path.dirname(__file__)
with open(path.join(root, "VERSION"), "r") as f:
    VERSION = f.read().strip()
with open(path.join(root, "README.md"), "r") as f:
    README = f.read().strip()

setup(
    name="lokii",
    version=VERSION,
    packages=find_packages(where="."),
    description="Generate, Load, Develop and Test with consistent relational datasets!",
    long_description=README,
    long_description_content_type="text/markdown",
    keywords="data generation, relational datasets, development environment, testing, database",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Typing :: Typed",
    ],
    author="Doruk Eren Aktaş",
    author_email="dorukerenaktas@gmail.com",
    entry_points={
        "console_scripts": ["lokii=lokii.cli:exec_cmd"],
    },
    url="https://github.com/dorukerenaktas/lokii",
    data_files=[("", ["VERSION"])],
    install_requires=[
        "pandas==2.0.1",
        "pathos==0.3.0",
        "tqdm==4.65.0",
        "duckdb==0.8.0",
        "typing==3.7.4.3",
    ],
    license="MIT License",
    zip_safe=False,
)
