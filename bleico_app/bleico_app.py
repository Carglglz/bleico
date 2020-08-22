# @Author: carlosgilgonzalez
# @Date:   2020-07-12T15:41:44+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2020-08-06T20:33:35+01:00
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

import logging
import sys
from bleico.systrayicon import SystemTrayIcon
import os
from bleico.devtools import load_dev
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

frozen = 'not'
if getattr(sys, 'frozen', False):
        # we are running in a bundle
        frozen = 'ever so'
        bundle_dir = sys._MEIPASS
else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))


SRC_PATH = os.path.join(bundle_dir, 'icons')
SRC_PATH_SOUND = os.path.join(bundle_dir, 'sounds')


#############################################

banner = """
$$$$$$$\  $$\       $$$$$$$$\ $$$$$$\  $$$$$$\   $$$$$$\\
$$  __$$\ $$ |      $$  _____|\_$$  _|$$  __$$\ $$  __$$\\
$$ |  $$ |$$ |      $$ |        $$ |  $$ /  \__|$$ /  $$ |
$$$$$$$\ |$$ |      $$$$$\      $$ |  $$ |      $$ |  $$ |
$$  __$$\ $$ |      $$  __|     $$ |  $$ |      $$ |  $$ |
$$ |  $$ |$$ |      $$ |        $$ |  $$ |  $$\ $$ |  $$ |
$$$$$$$  |$$$$$$$$\ $$$$$$$$\ $$$$$$\ \$$$$$$  | $$$$$$  |
\_______/ \________|\________|\______| \______/  \______/
    """
print('*'*60)
print(banner)
print('*'*60)

config_file_name = 'bleico_.config'
config_file_path = os.path.join(os.environ['HOME'], ".bleico")
device_is_configurated = config_file_name in os.listdir(config_file_path)
# Logging Setup

log_levels = {'debug': logging.DEBUG, 'info': logging.INFO,
              'warning': logging.WARNING, 'error': logging.ERROR,
              'critical': logging.CRITICAL}
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_levels['info'])
logging.basicConfig(
    level=log_levels['debug'],
    format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
    # format="%(asctime)s [%(name)s] [%(process)d] [%(threadName)s] [%(levelname)s]  %(message)s",
    handlers=[handler])
log = logging.getLogger('bleico')
log.info('Running bleico {}'.format('0.0.1'))


def main():
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    # Open Bledevice configuration
    if device_is_configurated:
        upy_conf = load_dev('bleico_', dir=config_file_path)
        if 'read_timeout' not in upy_conf.keys():
            upy_conf['read_timeout'] = 1
        if upy_conf is None:
            log.error("CONFIGURATION FILE NOT FOUND")
            sys.exit()
    # Create the icon

    icon = QIcon(os.path.join(SRC_PATH, "UNKNOWN.png"))
    icon.setIsMask(True)
    trayIcon = SystemTrayIcon(icon, device_uuid=upy_conf['uuid'],
                              logger=log, debug=True,
                              read_timeout=upy_conf['read_timeout'],
                              SRC_PATH=SRC_PATH, SRC_PATH_SOUND=SRC_PATH_SOUND)
    # Menu Update
    trayIcon.start_update_menu()

    trayIcon.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
