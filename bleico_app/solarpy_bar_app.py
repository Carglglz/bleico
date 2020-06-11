#!/usr/bin/env python3
# @Author: carlosgilgonzalez
# @Date:   2019-03-12T18:52:56+00:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-09-14T03:39:15+01:00
import sys
import os
import json
from upydevice import W_UPYDEVICE
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QTimer
global bundle_dir
frozen = 'not'
if getattr(sys, 'frozen', False):
        # we are running in a bundle
        frozen = 'ever so'
        bundle_dir = sys._MEIPASS
else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None,  device_ip=None, device_pass=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        # Create the menu
        self.menu = QMenu(parent)
        self.device_label = QAction("Esp8266/INA219")
        self.menu.addAction(self.device_label)
        self.separator = QAction()
        self.separator.setSeparator(True)
        self.menu.addAction(self.separator)
        self.bat_label = QAction("Battery")
        self.menu.addAction(self.bat_label)
        self.voltData = QAction("Voltage: ? V")
        self.menu.addAction(self.voltData)
        self.voltData.triggered.connect(self.refresh_menu)
        self.currData = QAction("Current: ? mA")
        self.menu.addAction(self.currData)
        self.PowerData = QAction("Power: ? mW")
        self.menu.addAction(self.PowerData)
        self.separator_bat = QAction()
        self.separator_bat.setSeparator(True)
        self.menu.addAction(self.separator_bat)
        self.solar_label = QAction("Solar")
        self.menu.addAction(self.solar_label)
        self.solar_voltData = QAction("Voltage: ? V")
        self.menu.addAction(self.solar_voltData)
        self.solar_voltData.triggered.connect(self.refresh_menu)
        self.solar_currData = QAction("Current: ? mA")
        self.menu.addAction(self.solar_currData)
        self.solar_PowerData = QAction("Power: ? mW")
        self.menu.addAction(self.solar_PowerData)
        self.separator_exit = QAction()
        self.separator_exit.setSeparator(True)
        self.menu.addAction(self.separator_exit)
        exitAction = self.menu.addAction("Exit")
        exitAction.triggered.connect(sys.exit)
        self.setContextMenu(self.menu)
        # Upydevice
        self.esp8266_device = W_UPYDEVICE(device_ip, device_pass)
        self.esp8266_device.cmd('led.on()', silent=True, bundle_dir=str(bundle_dir)+'/')
        # INA INIT
        # bme_lib = "bme280"
        # import_bme_cmd = "from {} import {};import init_BME280 as bme280;".format(
        #     bme_lib, bme_lib.upper())
        # bme_init_cmd = "my_bme = bme280.MY_BME280({},bme280.i2c);".format(
        #     bme_lib.upper())
        # bme_final_init = "my_bme.init()"
        # bme_init_cmd_str = import_bme_cmd + bme_init_cmd + bme_final_init
        # self.esp32_device.cmd(bme_init_cmd_str, silent=True)
        self.esp8266_device.cmd('led.off()', silent=True, bundle_dir=str(bundle_dir)+'/')

    def refresh_menu(self):
        self.esp8266_device.cmd('bat_data=[ina_BAT.voltage(),ina_BAT.current(),ina_BAT.power()];bat_data', silent=True, bundle_dir=str(bundle_dir)+'/')
        volt, current, power = self.esp8266_device.output
        # text = random.choice(["Odyssey", "Time", "Space"])
        self.voltData.setText("Voltage: {:.2f} V".format(volt))
        self.currData.setText("Current {:.2f} mA".format(current))
        self.PowerData.setText("Power: {:.2f} mW".format(power))

        self.esp8266_device.cmd('solar_data=[ina.voltage(),ina.current(),ina.power()];solar_data', silent=True, bundle_dir=str(bundle_dir)+'/')
        solar_volt, solar_current, solar_power = self.esp8266_device.output
        # text = random.choice(["Odyssey", "Time", "Space"])
        self.solar_voltData.setText("Voltage: {:.2f} V".format(solar_volt))
        self.solar_currData.setText("Current {:.2f} mA".format(solar_current))
        self.solar_PowerData.setText("Power: {:.2f} mW".format(solar_power))


def main():
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    # Open upydevice configuration
    file_conf = '{}/solarpy_.config'.format("{}/.upydevices".format(os.environ['HOME']))
    with open(file_conf, 'r') as config_file:
            upy_conf = json.loads(config_file.read())
    # Create the icon
    icon = QIcon(bundle_dir+'/'+"sunico.png")
    trayIcon = SystemTrayIcon(icon, device_ip=upy_conf['ip'], device_pass=upy_conf['passwd'])
    # Menu refresher
    timer = QTimer()
    timer.timeout.connect(trayIcon.refresh_menu)
    timer.start(5000)  # every 5 secs
    QTimer.singleShot(1000, trayIcon.refresh_menu)  # refresh on open

    trayIcon.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
