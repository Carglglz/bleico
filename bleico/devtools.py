#!/usr/bin/env python 3
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

import os
import json

dev_dir = '.bleico'
dev_path = os.path.join(os.environ['HOME'], dev_dir)


def setup_devs_dir(debug=False, name_dir=dev_dir):
    if name_dir not in os.listdir("{}".format(os.environ['HOME'])):
        os.mkdir(os.path.join(os.environ['HOME'], name_dir))
        if debug:
            print('{} directory created in HOME:{} directory'.format(name_dir, os.environ['HOME']))


def store_dev(name, ip=None, passwd=None, s_port=None, dir=dev_path,
              debug=False, **kargs):
    dev_ip = ip
    dev_pass = passwd
    dev_s_port = s_port
    dev_conf = {'ip': dev_ip, 'passwd': dev_pass,
                's_port': dev_s_port}
    file_conf = os.path.join(dir, '{}.config'.format(name))
    for key, val in kargs.items():
        if key not in dev_conf.keys():
            dev_conf[key] = val
    with open(file_conf, 'w') as config_file:
        config_file.write(json.dumps(dev_conf))
    if debug:
        print('device {} settings saved in {} directory!'.format(name, dir))


def load_dev(name, dir=dev_path, debug=False):
    try:
        file_conf = os.path.join(dir, '{}.config'.format(name))
        with open(file_conf, 'r') as config_file:
            dev_conf = json.loads(config_file.read())
        return dev_conf
    except Exception as e:
        if debug:
            print("CONFIGURATION FILE NOT FOUND")
        return None
