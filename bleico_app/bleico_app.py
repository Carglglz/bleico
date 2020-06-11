#!/usr/bin/env python3
# @Author: carlosgilgonzalez
# @Date:   2019-03-12T18:52:56+00:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-09-14T03:39:15+01:00

import logging
import sys
import bleico
import os
import argparse
import json
from binascii import hexlify
from upydevice import BLE_DEVICE
from upydevice.chars import ble_char_dict
from upydevice.devtools import store_dev, load_dev
import datetime
import time
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QSplashScreen
from PyQt5.QtCore import QTimer, QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot, Qt
from argcomplete.completers import ChoicesCompleter
import traceback
import darkdetect
import asyncio

frozen = 'not'
if getattr(sys, 'frozen', False):
        # we are running in a bundle
        frozen = 'ever so'
        bundle_dir = sys._MEIPASS
else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))


# THREAD WORKERS
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(object)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        # Return the result of the processing
        finally:
            self.signals.finished.emit()


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None, device_uuid=None, device_pass=None,
                 device_coms=None, battery_cap=None, solar_spec=None,
                 logger=None, debug=False, bundledir=bundle_dir):
        QSystemTrayIcon.__init__(self, icon, parent)
        self.debug = debug
        self.log = logger
        self.bundle_dir = bundledir
        # SPLASH SCREEN
        # Splash Screen
        self.splash_pix = QPixmap(self.bundle_dir+"/BlueL.png", 'PNG')
        self.scaled_splash = self.splash_pix.scaled(512, 512, Qt.KeepAspectRatio, transformMode = Qt.SmoothTransformation)
        self.splash = QSplashScreen(self.scaled_splash, Qt.WindowStaysOnTopHint)
        self.splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.splash.setEnabled(False)
        self.splash.show()
        self.splash.showMessage("Scanning for device...", Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
        # Upydevice
        self.esp32_device = BLE_DEVICE(device_uuid, init=True)
        while not self.esp32_device.is_connected():
            self.esp32_device = BLE_DEVICE(device_uuid, init=True)
            time.sleep(2)
        self.splash.clearMessage()
        # Create the menu
        # self.setIcon(QIcon(self.bundle_dir+"/{}_dark.png".format(self.esp32_device.appearance)))
        self.splash.showMessage("Device found", Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
        self.menu = QMenu(parent)
        # DEVICE INFO
        self.device_label = QAction("Device: ?")
        self.menu.addAction(self.device_label)
        self.uuid_menu = self.menu.addMenu("UUID")
        self.uuid_label = QAction("X")
        self.uuid_label.setEnabled(False)
        self.uuid_menu.addAction(self.uuid_label)
        self.separator = QAction()
        self.separator.setSeparator(True)
        self.menu.addAction(self.separator)
        # SERVICES
        self.serv_menu = self.menu.addMenu("Services")
        # self.serv_label.setEnabled(False)
        # self.serv_menu.addAction(self.serv_label)
        # main_serv = list(self.esp32_device.services_rsum.keys())[0]
        # main_serv_char = self.esp32_device.services_rsum[main_serv][0]
        # self.main_service = QAction("{} : {}".format(main_serv, main_serv_char))
        # self.serv_menu.addAction(self.main_service)
        for serv in self.esp32_device.services_rsum.keys():
            self.serv_action = self.serv_menu.addMenu("{}".format(serv))
            self.log.info(serv)
            for char in self.esp32_device.services_rsum[serv]:
                self.log.info(char)
                self.serv_action.addAction(char)
            # self.serv_menu.addAction(self.main_service)
        self.servs_separator = QAction()
        self.servs_separator.setSeparator(True)
        self.menu.addAction(self.servs_separator)
        self.serv_actions_dict = {serv: QAction(serv) for serv in self.esp32_device.services_rsum.keys()}
        self.serv_separator_dict = {}
        self.char_actions_dict = {}
        for key, serv in self.serv_actions_dict.items():
            serv.setEnabled(False)
            self.menu.addAction(serv)
            for char in self.esp32_device.services_rsum[key]:
                if char == 'Appearance':
                    self.char_actions_dict[char] = self.menu.addMenu("Appearance")
                    self.char_actions_dict[char].addAction(self.esp32_device.appearance)
                else:
                    self.char_actions_dict[char] = QAction("{}: ? ua".format(char))
                    self.menu.addAction(self.char_actions_dict[char])
            self.serv_separator_dict[key] = QAction()
            self.serv_separator_dict[key].setSeparator(True)
            self.menu.addAction(self.serv_separator_dict[key])
        self.separator_etc = QAction()
        self.separator_etc.setSeparator(True)
        self.menu.addAction(self.separator_etc)
        self.solar_label = QAction(QIcon(self.bundle_dir+"/bleico_dark.png"), "BLE")
        self.menu.addAction(self.solar_label)
        self.separator_exit = QAction()
        self.separator_exit.setSeparator(True)
        self.menu.addAction(self.separator_exit)
        self.exitAction = self.menu.addAction("Exit")
        self.exitAction.triggered.connect(self.exit_app)
        self.setContextMenu(self.menu)
        self.device_label.setText('Device: {}'.format(
            self.esp32_device.name))
        # self.esp8266_device.wr_cmd(
        #     'from machine import unique_id; unique_id()', silent=True)
        self.uuid_label.setText('{}'.format(self.esp32_device.UUID))
        # self.esp32_device.wr_cmd('led.on()', silent=True)
        self.dev_comsumption = device_coms
        self.battery_cap = battery_cap
        self.solar_spec = solar_spec
        self.batVOLT = 0
        self.batCURR = 0
        self.batPOW = 0
        self.solarVOLT = 0
        self.solarCURR = 0
        self.solarPOW = 0
        self.msg_log_battery = '[Battery] {}Voltage: {:.3f} V{}; {}Current: {:.3f} mA{}; Power: {:.3f} mW; Level: {} %; ETC: {}'
        self.msg_log_solar = '[Solar]   {}Voltage: {:.3f} V{}; {}Current: {:.3f} mA{}; Power: {:.3f} mW; Level: {} %'
        # Workers
        # self.timer.timeout.connect(self.refresh_menu)
        self.threadpool = QThreadPool()
        self.quit_thread = False
        if self.debug:
            self.log.info("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        if self.debug:
            self.log.info('Device: {}, UUID: {}'.format(self.esp32_device.name,
                                                        self.esp32_device.UUID))
        self.splash.clearMessage()
        self.splash.close()

    def set_dark_mode_ICON(self):
        self.setIcon(QIcon(self.bundle_dir+"/{}_dark.png".format(self.esp32_device.appearance)))

    def set_day_mode_ICON(self):
        self.setIcon(QIcon(self.bundle_dir+"/{}.png".format(self.esp32_device.appearance)))

    def autoset_icon(self, n):  # worker callback
        # self.theme = darkdetect.theme()
        # if int(datetime.now().strftime("%H")) < 20 and int(datetime.now().strftime("%H")) >= 8:
        #     self.set_day_mode_ICON()
        # if int(datetime.now().strftime("%H")) >= 20 or int(datetime.now().strftime("%H")) < 8:
        #     self.set_dark_mode_ICON()
        if n == 1:
            self.set_dark_mode_ICON()
        else:
            self.set_day_mode_ICON()

    def update_icon(self, progress_callback):  # in thread
        while True:
            if self.quit_thread:
                break
            else:
                self.theme = darkdetect.theme()
                # if int(datetime.now().strftime("%H")) < 20 and int(datetime.now().strftime("%H")) >= 8:
                #     self.set_day_mode_ICON()
                # if int(datetime.now().strftime("%H")) >= 20 or int(datetime.now().strftime("%H")) < 8:
                #     self.set_dark_mode_ICON()
                if self.theme == 'Dark':
                    progress_callback.emit(1)
                else:
                    progress_callback.emit(0)
            time.sleep(1)

    def start_update_icon(self):
        # Pass the function to execute
        worker = Worker(self.update_icon)  # Any other args, kwargs are passed to the run function
        # worker.signals.result.connect(self.print_output)
        # worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.autoset_icon)  # connect callback

        # Execute
        self.threadpool.start(worker)

    def refresh_menu(self, response):

        # data = self.esp32_device.read_service(key='Environmental Sensing', data_fmt="f")[0]
        data = response
        try:
            for char in data.keys():
                self.char_actions_dict[char].setText("{}: {:.2f} ua".format(char, data[char]))
                if self.debug:
                    for serv in self.esp32_device.services_rsum.keys():
                        if char in self.esp32_device.services_rsum[serv]:
                            self.log.info("{} [{}] : {:.2f} ua".format(serv, char, data[char]))
        except Exception as e:
            if self.debug:
                self.log.error(e)
        # # text = random.choice(["Odyssey", "Time", "Space"])
        # # Labels
        #
        # self.esp8266_device.wr_cmd(
        #     'solar_data=[ina.voltage(),ina.current(),ina.power()];solar_data',
        #     silent=True)
        # try:
        #     self.solarVOLT, self.solarCURR, self.solarPOW = self.esp8266_device.output
        #     solar_lp = round((self.solarPOW/self.solar_spec)*100)
        #
        #     if self.solarCURR < self.dev_comsumption:
        #         if self.solarVOLT < 4.3:
        #             solarVolt = [CRED, self.solarVOLT, CEND]
        #             solarCurr = ['', self.batCURR, '']
        #         else:
        #             solarVolt = [CGREEN, self.solarVOLT, CEND]
        #             solarCurr = ['', self.solarCURR, '']
        #     else:
        #         if self.solarVOLT < 4.3:
        #             solarVolt = [CRED, self.solarVOLT, CEND]
        #             solarCurr = ['', self.solarCURR, '']
        #         else:
        #             solarVolt = [CGREEN, self.solarVOLT, CEND]
        #             solarCurr = ['', self.solarCURR, '']
        #     if args.debug:
        #         self.log.info(self.msg_log_solar.format(*solarVolt, *solarCurr,
        #                                                 self.solarPOW, solar_lp))
        #     self.solar_label.setText('Solar: {:.0f} %'.format(solar_lp))
        #     self.solar_voltData.setText("Voltage: {:.2f} V".format(self.solarVOLT))
        #     self.solar_currData.setText("Current {:.2f} mA".format(self.solarCURR))
        #     self.solar_PowerData.setText("Power: {:.2f} mW".format(self.solarPOW))
        # except Exception as e:
        #     if args.debug:
        #         self.log.error(e)
        # text = random.choice(["Odyssey", "Time", "Space"])

    def update_menu(self, progress_callback):
        while True:
            if self.quit_thread:
                break
            else:
                try:
                    data = {}
                    for char in self.esp32_device.readables.keys():
                        if char != 'Appearance':
                            data[char] = (self.esp32_device.read_service(key=char,
                                                                       data_fmt="f")[0])
                    progress_callback.emit(data)
                except Exception as e:
                    progress_callback.emit(False)
            time.sleep(1)

    def start_update_menu(self):
        # Pass the function to execute
        worker_menu = Worker(self.update_menu) # Any other args, kwargs are passed to the run function
        # worker.signals.result.connect(self.print_output)
        # worker.signals.finished.connect(self.thread_complete)
        # worker.signals.progress.connect(self.progress_fn)
        worker_menu.signals.progress.connect(self.refresh_menu)

        # Execute
        self.threadpool.start(worker_menu)

    def shutdown(self, loop):
        # self.log.info("Shutdown...")

        try:
            loop.stop()
        except Exception as e:
            # print(e)
            pass
        # Find all running tasks:
        try:
            pending = asyncio.all_tasks(loop)

        # Run loop until tasks done:
            loop.run_until_complete(asyncio.gather(*pending))
        except Exception as e:
            # print(e)
            pass

        self.log.info("Shutdown complete...")
        try:
            self.esp32_device.disconnect()
        except Exception as e:
            # print(e)
            pass

    def exit_app(self):
        if self.debug:
            self.log.info('Closing now...')
            self.log.info('Done!')
            self.log.info('Shutdown pending tasks...')
        self.quit_thread = True
        self.log.info("{}".format(self.esp32_device.loop.is_running()))
        if self.esp32_device.loop.is_running():
            self.shutdown(self.esp32_device.loop)
        # self.esp32_device.loop.stop()
        # Run loop until tasks done
        else:
            try:
                self.esp32_device.disconnect()
            except Exception as e:
                pass
        time.sleep(2)
        sys.exit()


config_file_name = 'bleico_.config'
config_file_path = "{}/.upydevices".format(os.environ['HOME'])
device_is_configurated = config_file_name in os.listdir(config_file_path)
# Logging Setup

# filelog_path = "{}/.upydevices_logs/weatpyfluxd_logs/".format(
#     os.environ['HOME'])
log_levels = {'debug': logging.DEBUG, 'info': logging.INFO,
              'warning': logging.WARNING, 'error': logging.ERROR,
              'critical': logging.CRITICAL}
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_levels['error'])
logging.basicConfig(
    level=log_levels['debug'],
    format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
    # format="%(asctime)s [%(name)s] [%(process)d] [%(threadName)s] [%(levelname)s]  %(message)s",
    handlers=[handler])
log = logging.getLogger('bleico')  # setup one logger per device
# log.setLevel(log_levels[args.dslev]) # MASTER LOG LEVEL
# # Filehandler for error
# fh_err = logging.FileHandler(''.join([filelog_path, 'weatpyfluxd_error.log']))
# fh_err.setLevel(log_levels[args.dflev])
# # Formatter for errors
# fmt_err = logging.Formatter(
#     "%(asctime)s [%(name)s] [%(process)d] [%(threadName)s] [%(levelname)s]  %(message)s")
# fh_err.setFormatter(fmt_err)
# log.addHandler(fh_err)
log.info('Running bleico {}'.format('0.0.1'))


def main():
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    # Open upydevice configuration
    if device_is_configurated:
        upy_conf = load_dev('bleico_')
        if upy_conf is None:
            log.error("CONFIGURATION FILE NOT FOUND")
            sys.exit()

    # Create the icon
    if not darkdetect.isDark():
        icon = QIcon(bundle_dir+"/Bluelogo_dark.png")
    else:
        icon = QIcon(bundle_dir+"/Bluelogo.png")
    trayIcon = SystemTrayIcon(icon, device_uuid=upy_conf['uuid'],
                              device_coms=upy_conf['Dev_C'],
                              battery_cap=upy_conf['Bat_C'],
                              solar_spec=upy_conf['Solar_sp'],
                              logger=log, debug=True)
    # Menu refresher
    # timer = QTimer()
    # timer.timeout.connect(trayIcon.refresh_menu)
    # timer.start(1000)  # every 5 secs
    # QTimer.singleShot(10, trayIcon.refresh_menu)  # refresh on open
    trayIcon.start_update_icon()
    trayIcon.start_update_menu()

    trayIcon.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()