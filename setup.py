#!/usr/bin/env python

from pathlib import Path

from setuptools import setup, find_packages

root = Path(__file__).resolve().parent
VERSION = (root / "VERSION").read_text(encoding="utf-8").strip()
README = (root / "README.md").read_text(encoding="utf-8")

setup(
    name="lokii",
    version=VERSION,
    packages=find_packages(where="."),
    description="Generate, Load, Develop and Test with consistent relational datasets!",
    long_description=README,
    keywords="data generation, relational datasets, development environment, testing, database",
    classifiers=[
        "Development Status :: 4 - Beta",
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
    py_modules=["lokii"],
    entry_points={
        "console_scripts": ["lokii=lokii.cli:exec_cmd"],
    },
    url="https://github.com/dorukerenaktas/lokii",
    data_files=[("", ["VERSION"])],
    install_requires=[
        "pandas==2.0.1",
        "pathos==0.3.0",
        "networkx==3.1",
        "tqdm==4.65.0",
        "duckdb==0.8.0",
        "typing==3.7.4.3",
        "typing-extensions==4.6.2",
    ],
    license="MIT License",
    zip_safe=False,
)
