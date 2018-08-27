#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name='gpo-zugaina-dl',
	version='0.0.1',
	description='Search and downalod ebuild from http://gpo.zugaina.org',
	author='Marco Genasci',
	author_email='fedeliallalinea@gmail.com',
	url='https://github.com/fedeliallalinea/gpo-zugaina-dl',
	packages=['gpo_zugaina_dl', 'gpo_zugaina_dl/colors'],
	scripts=['bin/gpo-zugaina-dl'],
#	long_description=read('README.md'),
	project_urls={
        'Bug Reports': 'https://github.com/fedeliallalinea/gpo-zugaina-dl/issues',
        'Source': 'https://github.com/fedeliallalinea/gpo-zugaina-dl',
	}
)
