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

setup(name='bleico',
      version='0.0.1',
      description='Bluetooth Low Energy System Tray App',
      url='http://github.com/cgglz/bleico',
      author='Carlos Gil Gonzalez',
      author_email='carlosgilglez@gmail.com',
      license='MIT',
      packages=['bleico'],
      zip_safe=False,
      include_package_data=True,
      scripts=['bleico_dir/bin/bleico'],
      install_requires=['bleak>=0.7.1', 'PyQt5', 'bleak_sigspec'])
