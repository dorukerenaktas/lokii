#!/usr/bin/env python
from pathlib import Path

from setuptools import setup, find_packages

root = Path(__file__).resolve().parent
VERSION = (root / "VERSION").read_text(encoding="utf-8").strip()

setup(
    name="lokii",
    version=VERSION,
    packages=find_packages(where="."),
    description="CSV dataset generator",
    author="Package Author",
    author_email="you@youremail.com",
    keywords="boilerplate package",
    py_modules=["lokii"],
    entry_points={
        "console_scripts": ["lokii=lokii.cli:execute_command_line"],
    },
    url="http://path-to-my-packagename",
    install_requires=[
        "pandas~=2.0.1",
        "pathos~=0.3.0",
        "networkx~=3.1",
        "tqdm~=4.65.0",
        "duckdb~=0.8.0",
    ],
    license="MIT License",
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.8",
    ],
)
