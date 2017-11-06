# coding: utf-8

import os, sys
from setuptools import setup, find_packages

NAME = "edam2json"
VERSION = "dev"

SETUP_DIR = os.path.dirname(__file__)
README = os.path.join(SETUP_DIR, 'README.md')
readme = open(README).read()

REQUIRES = ["rdflib", "rdflib-jsonld"]

setup(
    name=NAME,
    version=VERSION,
    description="edam2json automates the export of the EDAM ontology to various JSON-based formats",
    author='Hervé Ménager',
    author_email="hmenager@pasteur.fr",
    url="https://github.com/edamontology/edam2json",
    packages=find_packages(),
    install_requires=REQUIRES,
    license="MIT",
    keywords=["Bioinformatics", "OWL", "JSON", "JSON-LD", "Ontology"],
    entry_points={
        'console_scripts': [
            'edam2json=edam2json.__main__:main',
        ]
    }
)
