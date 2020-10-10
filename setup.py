#!/usr/bin/env python3
# @Author: carlosgilgonzalez
# @Date:   2020-07-12T15:41:44+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2020-07-12T17:13:27+01:00

"""
Copyright (c) 2020 Carlos G. Gonzalez and others (see the AUTHORS file).
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from setuptools import setup


def readme():
    with open('README.md', 'r', encoding="utf-8") as f:
        return f.read()


setup(name='bleico',
      version='0.0.2',
      description='Bluetooth Low Energy System Tray App',
      long_description=readme(),
      long_description_content_type='text/markdown',
      url='http://github.com/Carglglz/bleico',
      author='Carlos Gil Gonzalez',
      author_email='carlosgilglez@gmail.com',
      classifiers=[
                  'Intended Audience :: Developers',
                  'Intended Audience :: Science/Research',
                  'Intended Audience :: Education',
                  'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                  'Programming Language :: Python :: 3.7',
                  'Programming Language :: Python :: 3.8',
                  'Topic :: System :: Monitoring',
                  'Topic :: Scientific/Engineering',
                  'Topic :: Software Development :: Embedded Systems'],
      license='GPL-3.0',
      packages=['bleico'],
      zip_safe=False,
      include_package_data=True,
      scripts=['bleico_cli/bin/bleico'],
      install_requires=['bleak>=0.8.0', 'PyQt5', 'bleak_sigspec>=0.0.4'])
