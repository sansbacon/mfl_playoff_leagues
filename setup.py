# mfl_playoff_leagues/setup.py
# -*- coding: utf-8 -*-
# Copyright (C) 2022 Eric Truett
# Licensed under the MIT License

"""
setup.py

installation script
"""

from setuptools import setup, find_packages

PACKAGE_NAME = "mfl_playoff_leagues"


def run():
    setup(name=PACKAGE_NAME,
          version="0.1",
          description="python library for managing MFL playoff leagues",
          author="Eric Truett",
          author_email="eric@erictruett.com",
          packages=find_packages('src'),
          package_dir={'': 'src'},
          include_package_data=True,          
          zip_safe=False)


if __name__ == '__main__':
    run()
