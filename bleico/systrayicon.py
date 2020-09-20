#!/usr/bin/env python3
# @Author: carlosgilgonzalez
# @Date:   2020-07-12T15:41:44+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2020-08-06T20:55:33+01:00

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

import sys
import threading
from bleico.socket_client_server import socket_server
from bleak_sigspec.utils import get_char_value, pformat_char_value
import os
from bleico.ble_device import BLE_DEVICE  # get own ble_device
from bleico.set_value_dialog import SetValueDialog
from bleico.set_tooltip_dialog import ChecklistDialog
from bleico.ble_scanner_widget import BleScanner
from bleico.characteristic_metadata_widget import CharacteristicViewer
# from bleico.console_log import QPlainTextEditLogger
from PyQt5.QtCore import QCoreApplication
from datetime import datetime
import time
import struct
from PyQt5.QtGui import QIcon, QPixmap, QDesktopServices
from PyQt5.QtWidgets import (QSystemTrayIcon, QMenu, QAction,
                             QSplashScreen)
from PyQt5.QtCore import (QObject, QRunnable, QThreadPool, pyqtSignal,
                          pyqtSlot, Qt, QUrl)
from PyQt5.QtMultimedia import QSound
import traceback
import asyncio
from array import array


class DisconnectionError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'DisconnectionError, {0} '.format(self.message)
        else:
            return 'DisconnectionError has been raised'


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
    def __init__(self, icon, parent=None, device_uuid=None,
                 logger=None, max_tries=0, read_timeout=1,
                 SRC_PATH=None, SRC_PATH_SOUND=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        self.log = logger
        # CONSOLE LOG # TODO:  MAKE THREAD SAFE (EMIT SIGNAL)
        # self.console_logger = QPlainTextEditLogger()
        # self.console_logger.setFormatter(logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s] %(message)s"))
        # self.log.addHandler(self.console_logger)
        self._ntries = 0
        self._read_timeout = read_timeout
        self._timeout_count = read_timeout - 1
        self._rssi_buffer = array('h', (0 for _ in range(10)))
        # SPLASH SCREEN
        self.splash_pix = QPixmap(os.path.join(SRC_PATH, "bleico.png"), 'PNG')
        self.scaled_splash = self.splash_pix.scaled(
            512, 512, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        self.splash = QSplashScreen(
            self.scaled_splash, Qt.WindowStaysOnTopHint)
        self.splash.setWindowFlags(
            Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.splash.setEnabled(False)
        self.splash.show()
        self.splash.showMessage("Scanning for device...",
                                Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
        # Bledevice
        self.esp32_device = BLE_DEVICE(device_uuid, init=True, log=self.log)
        while not self.esp32_device.connected:
            if self._ntries <= max_tries:
                self.esp32_device = BLE_DEVICE(device_uuid, init=True, log=self.log)
                time.sleep(0.5)
                self._ntries += 1
            else:
                self.log.error("Device {} not found".format(device_uuid))
                self.splash.clearMessage()
                self.splash.showMessage("Device {} not found".format(device_uuid),
                                        Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
                # time.sleep(2)
                self.splash.clearMessage()
                self.splash.close()
                Scanner = BleScanner(SRC_PATH=SRC_PATH, log=self.log)
                while not self.esp32_device.connected:
                    Scanner.show()
                    Scanner.raise_()
                    while Scanner.device_to_connect is None:
                        QCoreApplication.processEvents()

                    if Scanner.device_to_connect != 'CANCEL':
                        self.log.info('Connecting to device {} ...'.format(Scanner.device_to_connect))
                        self.esp32_device = BLE_DEVICE(Scanner.device_to_connect,
                                                       init=True, log=self.log)
                        if self.esp32_device.connected:
                            Scanner.hide()
                            break
                        else:
                            Scanner.device_to_connect = None
                    else:
                        sys.exit()
                Scanner.hide()
        self.splash.clearMessage()
        # Get RSSI
        _rssi_init_val = self.esp32_device.get_RSSI()
        for i in range(len(self._rssi_buffer)):
            self._rssi_buffer[i] = _rssi_init_val
        # Create the menu
        if "{}.png".format(self.esp32_device.appearance_tag) not in os.listdir(SRC_PATH):
            self.app_icon = QIcon(os.path.join(SRC_PATH, "UNKNOWN.png"))
        else:
            self.app_icon = QIcon(os.path.join(SRC_PATH, "{}.png".format(self.esp32_device.appearance_tag)))
        self.app_icon.setIsMask(True)
        self.setIcon(self.app_icon)
        self.splash.showMessage("Device {} found".format(self.esp32_device.name),
                                Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
        self.menu = QMenu(parent)
        # DEVICE INFO
        self.device_label = QAction('Device: {}'.format(
            self.esp32_device.name))

        self.menu.addAction(self.device_label)
        self.uuid_menu = self.menu.addMenu("UUID")
        self.uuid_label = QAction('{}'.format(self.esp32_device.UUID))
        self.uuid_label.setEnabled(False)
        self.uuid_menu.addAction(self.uuid_label)
        self.separator = QAction()
        self.separator.setSeparator(True)
        self.menu.addAction(self.separator)
        # SERVICES & CHARS
        # AVOID READ CHARS
        self.avoid_chars = ['Appearance', 'Manufacturer Name String',
                            'Battery Power State', 'Model Number String',
                            'Firmware Revision String', 'Serial Number String',
                            'Hardware Revision String',
                            'Software Revision String']
        self.avoid_field_strings = ['Measurement', 'Value', 'String',
                                    '(uint8)', '(uint16)', 'Compound']

        self.metadata_chars = {}
        self.metadata_chars_view = {}

        self.serv_menu = self.menu.addMenu("Services")

        self.log.info("Device {} found".format(self.esp32_device.name))
        self.log.info("Services:")
        for serv in self.esp32_device.services_rsum.keys():
            self.serv_action = self.serv_menu.addMenu("{}".format(serv))
            self.log.info(" (S) {}".format(serv))
            for char in self.esp32_device.services_rsum[serv]:
                self.log.info(" (C)  - {}".format(char))
                self.metadata_chars[char] = self.serv_action.addAction(char)
                self.metadata_chars[char].triggered.connect(self.check_which_triggered_view)
                try:
                    metadata_char = self.esp32_device.chars_xml[char]
                    self.metadata_chars_view[char] = CharacteristicViewer(char=metadata_char)
                except Exception as e:
                    self.log.error(traceback.format_exc())

        self.servs_separator = QAction()
        self.servs_separator.setSeparator(True)
        self.menu.addAction(self.servs_separator)
        self.serv_actions_dict = {serv: QAction(serv) for serv in self.esp32_device.services_rsum.keys()}
        self.serv_separator_dict = {}
        self.char_actions_dict = {}
        self.notify_char_menu_dict = {}
        self.notify_char_actions_dict = {}
        self.toggle_desktop_notify_char_actions_dict = {}
        self.do_desktop_notify_char_dict = {}
        self.write_char_menu_dict = {}
        self.write_char_actions_dict = {}
        self.battery_power_state_actions_dict = {}
        self.char_fields_actions_dict = {}
        self.char_fields_bitfields_actions_dict = {}
        self.checklist_fields = []
        self.checklist_choices = []
        self.tooltip_h_ch_field_values_dict = {}
        for key, serv in self.serv_actions_dict.items():
            if key == 'Device Information':
                self.log.info('Device: {}, UUID: {}'.format(self.esp32_device.name,
                                                            self.esp32_device.UUID))
                self.log.info('Device Information:')
                self.devinfo_menu = self.menu.addMenu(key)
                for char_handle in self.esp32_device.services_rsum_handles[key]:
                    char = self.esp32_device.readables_handles[char_handle]
                    try:
                        self.char_actions_dict[char_handle] = self.devinfo_menu.addAction("{}: {}".format(char.replace('String', ''), self.esp32_device.device_info[char]))
                        self.char_actions_dict[char_handle].setEnabled(False)
                        self.log.info("    - {}: {}".format(char.replace('String', ''), self.esp32_device.device_info[char]))
                    except Exception as e:
                        self.log.error(traceback.format_exc())
                self.menu.addSeparator()
            else:
                pass
        for key, serv in self.serv_actions_dict.items():
            if key == 'Device Information':
                pass
            else:
                serv.setEnabled(False)
                self.menu.addAction(serv)
                for char_handle in self.esp32_device.services_rsum_handles[key]:
                    if char_handle in self.esp32_device.readables_handles.keys() or char_handle in self.esp32_device.notifiables_handles.keys():
                        try:
                            char = self.esp32_device.readables_handles[char_handle]
                        except Exception as e:
                            char = self.esp32_device.notifiables_handles[char_handle]
                        if char in self.avoid_chars:
                            if char == 'Battery Power State':
                                self.char_actions_dict[char_handle] = self.menu.addMenu(char)
                                for state, value in self.esp32_device.batt_power_state.items():
                                    self.battery_power_state_actions_dict[state]=self.char_actions_dict[char_handle].addAction("{}: {}".format(state,value))  # store actions in dict to update
                            else:
                                self.char_actions_dict[char_handle] = self.menu.addMenu(char)
                                self.char_actions_dict[char_handle].addAction(self.esp32_device.device_info[char])
                        else:
                            self.tooltip_h_ch_field_values_dict[char_handle] = {char: {}}
                            # HERE DIVIDE CHARS INTO SINGLE/FEATURES/MULTIPLE
                            # SINGLE FIELD CHARACTERISTIC
                            if len(self.esp32_device.chars_xml[char].fields) == 1:
                                bfield = False
                                for field in self.esp32_device.chars_xml[char].fields:
                                    if 'BitField' in self.esp32_device.chars_xml[char].fields[field]:
                                        bfield = True
                                if not bfield:
                                    self.char_actions_dict[char_handle] = QAction("{}: ? ua".format(char))
                                    self.menu.addAction(self.char_actions_dict[char_handle])
                                    # ADD TO CHECKLIST
                                    for field in self.esp32_device.chars_xml[char].fields:
                                        self.checklist_fields.append("{}:{}:{}".format(char, field, char_handle))
                                        self.tooltip_h_ch_field_values_dict[char_handle][char][field] = ''
                                else:
                                    self.char_actions_dict[char_handle] = self.menu.addMenu(char)
                                    self.char_fields_actions_dict[char_handle] = {}
                                    for field in self.esp32_device.chars_xml[char].fields:
                                        if 'BitField' in self.esp32_device.chars_xml[char].fields[field]:
                                            for _bitfield in self.esp32_device.chars_xml[char].fields[field]['BitField']:
                                                self.char_fields_actions_dict[char_handle][_bitfield] = self.char_actions_dict[char_handle].addAction(_bitfield)
                                                # ADD TO CHECKLIST
                                                self.checklist_fields.append("{}:{}:{}".format(char, _bitfield, char_handle))
                                                self.tooltip_h_ch_field_values_dict[char_handle][char][_bitfield] = ''

                            # MULTIPLE FIELDS CHARACTERISTIC
                            elif len(self.esp32_device.chars_xml[char].fields) > 1:
                                self.char_actions_dict[char_handle] = self.menu.addMenu(char)
                                self.char_fields_actions_dict[char_handle] = {}
                                self.char_fields_bitfields_actions_dict[char_handle] = {}
                                for field in self.esp32_device.chars_xml[char].fields:
                                    bfield = False
                                    if 'BitField' in self.esp32_device.chars_xml[char].fields[field]:
                                            if field != 'Flags':
                                                bfield = True
                                    if not bfield:
                                        self.char_fields_actions_dict[char_handle][field] = self.char_actions_dict[char_handle].addAction(field)
                                        # ADD TO CHECKLIST
                                        self.checklist_fields.append("{}:{}:{}".format(char, field, char_handle))
                                        self.tooltip_h_ch_field_values_dict[char_handle][char][field] = ''
                                    else:
                                        self.char_fields_actions_dict[char_handle][field] = self.char_actions_dict[char_handle].addMenu(field)
                                        self.char_fields_bitfields_actions_dict[char_handle][field] = {}
                                        for _bitfield in self.esp32_device.chars_xml[char].fields[field]['BitField']:
                                            self.char_fields_bitfields_actions_dict[char_handle][field][_bitfield] = self.char_fields_actions_dict[char_handle][field].addAction(_bitfield)
                                            # ADD TO CHECKLIST
                                            self.checklist_fields.append("{}:{}:{}".format(char, _bitfield, char_handle))
                                            self.tooltip_h_ch_field_values_dict[char_handle][char][_bitfield] = ''

                    if char_handle in self.esp32_device.writeables_handles.keys():
                        char = self.esp32_device.writeables_handles[char_handle]
                        xml_char = self.esp32_device.chars_xml[char]
                        if len(xml_char.fields) == 1:
                            self.write_char_menu_dict[char_handle] = self.menu.addMenu("Set {}".format(char))
                            for field in xml_char.fields:
                                if 'Enumerations' in xml_char.fields[field].keys() and 'BitField' not in xml_char.fields[field].keys():
                                    self.write_char_actions_dict[char_handle] = {}
                                    for k, v in xml_char.fields[field]['Enumerations'].items():
                                        self.write_char_actions_dict[char_handle][v] = self.write_char_menu_dict[char_handle].addAction(v)
                                        self.write_char_actions_dict[char_handle][v].triggered.connect(self.check_which_triggered_write)
                                else:
                                    # SET VALUE
                                    self.write_char_actions_dict[char_handle] = {}
                                    self.write_char_actions_dict[char_handle]["set_value"] = self.write_char_menu_dict[char_handle].addAction(
                                        "Set Value")
                                    self.write_char_actions_dict[char_handle]["set_value"].triggered.connect(
                                        self.check_which_triggered_write)
                                    self.write_char_actions_dict[char_handle]["set_value_box"] = SetValueDialog(
                                        char=xml_char, char_handle=char_handle, log=self.log, dev=self.esp32_device)
                        else:
                            # SET VALUE
                            self.write_char_actions_dict[char_handle] = {}
                            if char_handle in self.char_actions_dict:
                                self.char_actions_dict[char_handle].addSeparator()
                                self.write_char_actions_dict[char_handle]["set_value"] = self.char_actions_dict[char_handle].addAction(
                                    "Set Value")
                            else:
                                self.write_char_menu_dict[char_handle] = self.menu.addMenu(char)
                                self.write_char_actions_dict[char_handle]["set_value"] = self.write_char_menu_dict[char_handle].addAction(
                                    "Set Value")
                            self.write_char_actions_dict[char_handle]["set_value"].triggered.connect(
                                self.check_which_triggered_write)
                            self.write_char_actions_dict[char_handle]["set_value_box"] = SetValueDialog(
                                char=xml_char, char_handle=char_handle, log=self.log, dev=self.esp32_device)

                self.serv_separator_dict[key] = QAction()
                self.serv_separator_dict[key].setSeparator(True)
                self.menu.addAction(self.serv_separator_dict[key])
        self.separator_etc = QAction()
        self.separator_etc.setSeparator(True)
        self.menu.addAction(self.separator_etc)
        # NOTIFY
        self.notify_menu = self.menu.addMenu("Notify")
        for char_handle in self.esp32_device.notifiables_handles.keys():
            char = self.esp32_device.notifiables_handles[char_handle]
            self.notify_char_menu_dict[char_handle] = self.notify_menu.addMenu(char)
            self.notify_char_actions_dict[char_handle] = self.notify_char_menu_dict[char_handle].addAction('Notify')
            self.notify_char_actions_dict[char_handle].triggered.connect(self.check_which_triggered)
            self.toggle_desktop_notify_char_actions_dict[char_handle] = self.notify_char_menu_dict[char_handle].addAction('Desktop Notification: On')
            self.do_desktop_notify_char_dict[char_handle] = True
            self.toggle_desktop_notify_char_actions_dict[char_handle].triggered.connect(self.toggle_desktop_notify)
            # here trigger action --> set flag notify True, start Thread, callback notify ...
        self.notify_menu.addSeparator()
        self.notify_sound_act = QAction("Sound: Disabled")
        self.notify_sound_act.setEnabled(True)
        self.notify_menu.addAction(self.notify_sound_act)
        self.notify_sound_act.triggered.connect(self.toggle_notify_sound)
        self.notify_status_act = QAction("Status: Enabled")
        self.notify_menu.addAction(self.notify_status_act)
        self.notify_status_act.triggered.connect(self.toggle_notify_status)
        self.menu.addSeparator()
        # SET TOOL TIP DIALOG
        self.set_tool_tip_dialog = ChecklistDialog('Set Tool Tip Fields',
                                                   self.checklist_fields,
                                                   checked=False, log=self.log,
                                                   check_list=self.checklist_choices)
        self.set_tool_tip_action = QAction("Set Tool Tip")
        self.set_tool_tip_action.triggered.connect(self.show_checklist_dialog)
        self.menu.addAction(self.set_tool_tip_action)
        # TIME LAST UPDATE
        self.menu.addSeparator()
        self.last_update_action = QAction()
        self.last_update_action.setEnabled(False)
        self.menu.addAction(self.last_update_action)
        # STATUS
        self.device_status_action = QAction("Status: Connected")
        self.device_status_action.setEnabled(False)
        self.menu.addAction(self.device_status_action)
        # RSSI
        self.device_rssi_action = QAction("RSSI: ? dBm")
        self.device_rssi_action.setEnabled(False)
        self.menu.addAction(self.device_rssi_action)
        self.menu.addSeparator()
        # CONSOLE
        # self.console_log_action = QAction('Console')
        # self.console_log_action.triggered.connect(self.show_console)
        # self.menu.addAction(self.console_log_action)
        # self.menu.addSeparator()
        # ABOUT
        self.about_action = QAction("About")
        self.about_action.triggered.connect(self.about_url)
        self.menu.addAction(self.about_action)
        # EXIT
        self.separator_exit = QAction()
        self.separator_exit.setSeparator(True)
        self.menu.addAction(self.separator_exit)
        self.exitAction = self.menu.addAction("Exit")
        self.exitAction.triggered.connect(self.exit_app)
        self.setContextMenu(self.menu)
        # Workers
        self.threadpool = QThreadPool()
        self.quit_thread = False
        self.main_server = None
        self.log.info("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.splash.clearMessage()
        self.splash.close()

        # NOTIFIABLE
        self.char_to_notify = None
        self.chars_to_notify = []
        self.chars_to_notify_handles = []
        self.notify_is_on = False
        self.notify_sound_is_on = False
        self.notify_loop = asyncio.new_event_loop()
        self.notify_type_icon = {'Info': QSystemTrayIcon.Information,
                                 'Warning': QSystemTrayIcon.Warning,
                                 'Critical': QSystemTrayIcon.Critical}
        self.notify_sound = QSound(os.path.join(SRC_PATH_SOUND, "definite.wav"))
        self.notify_status_is_on = True

        # Disconnection callback
        self.esp32_device.set_disconnected_callback(self.esp32_device.disconnection_callback)

        # ON EXIT
        self.menu_thread_done = False
        self.notify_thread_done = True

    def toggle_notify_sound(self):
        self.notify_sound_is_on = not self.notify_sound_is_on
        if self.notify_sound_is_on:
            self.notify_sound_act.setText("Sound: Enabled")
            self.log.info('Notification Sound: Enabled')
        else:
            self.notify_sound_act.setText("Sound: Disabled")
            self.log.info('Notification Sound: Disabled')

    def toggle_notify_status(self):
        self.notify_status_is_on = not self.notify_status_is_on
        if self.notify_status_is_on:
            self.notify_status_act.setText("Status: Enabled")
            self.log.info('Notification on Status change: Enabled')
        else:
            self.notify_status_act.setText("Status: Disabled")
            self.log.info('Notification on Status change: Disabled')

    def check_which_triggered(self, checked):
        action = self.sender()
        for char_handle in self.notify_char_actions_dict.keys():
            char = self.esp32_device.notifiables_handles[char_handle]
            if action == self.notify_char_actions_dict[char_handle]:
                if char_handle not in self.chars_to_notify_handles:
                    self.log.info("Char: {} Notification Enabled".format(char))
                    self.char_to_notify = char
                    self.chars_to_notify.append(char)
                    self.chars_to_notify_handles.append(char_handle)
                    action.setText('Stop Notification')
                    if self.main_server:
                        self.main_server.send_message("start:{}:{}".format(char_handle, char))
                    else:
                        self.start_notify_char()
                        self.notify_is_on = True
                else:
                    self.log.info("Char: {} Notification Disabled".format(char))
                    self.chars_to_notify.remove(char)
                    self.chars_to_notify_handles.remove(char_handle)
                    self.main_server.send_message("stop:{}:{}".format(char_handle, char))
                    action.setText('Notify')

    def check_which_triggered_write(self, checked):
        action = self.sender()
        for char_handle in self.write_char_actions_dict.keys():
            char = self.esp32_device.writeables_handles[char_handle]
            for write_action_key in self.write_char_actions_dict[char_handle].keys():
                if action == self.write_char_actions_dict[char_handle][write_action_key]:
                    xml_char = self.esp32_device.chars_xml[char]
                    self.log.info('Writing to {}'.format(char))
                    if len(xml_char.fields) == 1:
                        format = ""
                        val_to_write = []
                        for field in xml_char.fields:
                            if 'Unit' not in xml_char.fields[field].keys() and 'Enumerations' in xml_char.fields[field].keys():
                                if 'BitField' not in xml_char.fields[field].keys():
                                    try:
                                        map_write_values = {v: int(k) for k, v in xml_char.fields[field]['Enumerations'].items()}
                                        val_to_write.append(map_write_values[write_action_key])
                                        format += xml_char.fields[field]['Ctype']
                                        self.log.info('{}: {}'.format(char, write_action_key))
                                    except Exception as e:
                                        self.log.error(e)
                                    try:
                                        packed_val = struct.pack(format, *val_to_write)
                                        self.esp32_device.write_char(xml_char.name,
                                                                     data=packed_val,
                                                                     handle=char_handle)
                                    except Exception as e:
                                        self.log.error(e)
                                else:
                                    self.log.info('Showing {} Set Value Control'.format(char))
                                    self.write_char_actions_dict[char_handle]["set_value_box"].show()
                                    self.write_char_actions_dict[char_handle]["set_value_box"].raise_()
                            else:
                                self.log.info('Showing {} Set Value Control'.format(char))
                                self.write_char_actions_dict[char_handle]["set_value_box"].show()
                                self.write_char_actions_dict[char_handle]["set_value_box"].raise_()
                    else:
                        self.log.info('Showing {} Set Value Control'.format(char))
                        self.write_char_actions_dict[char_handle]["set_value_box"].show()
                        self.write_char_actions_dict[char_handle]["set_value_box"].raise_()

    def check_which_triggered_view(self, checked):
        action = self.sender()
        for char in self.metadata_chars_view:
            if action == self.metadata_chars[char]:
                self.log.info('Showing {} Metadata View'.format(char))
                self.metadata_chars_view[char].show()
                self.metadata_chars_view[char].raise_()

    def toggle_desktop_notify(self, checked):
        action = self.sender()
        for char_handle in self.notify_char_actions_dict.keys():
            char = self.esp32_device.notifiables_handles[char_handle]
            if action == self.toggle_desktop_notify_char_actions_dict[char_handle]:
                value = not self.do_desktop_notify_char_dict[char_handle]
                self.do_desktop_notify_char_dict[char_handle] = value
                if value:
                    self.log.info("Char: {} Desktop Notification Enabled".format(char))
                    self.toggle_desktop_notify_char_actions_dict[char_handle].setText('Desktop Notification: On')
                else:
                    self.log.info("Char: {} Desktop Notification Disabled".format(char))
                    self.toggle_desktop_notify_char_actions_dict[char_handle].setText('Desktop Notification: Off')

    def refresh_menu(self, response):

        data = response
        if data == 'finished':
            self.log.info("MENU CALLBACK: THREAD FINISH RECEIVED")
            self.menu_thread_done = True
        elif data == 'disconnected':
            if self.notify_status_is_on:
                self.notify("Disconnection event", 'Device {} is now disconnected'.format(self.esp32_device.name))
            for char_handle in self.esp32_device.notifiables_handles:
                char = self.esp32_device.notifiables_handles[char_handle]
                self.notify_char_actions_dict[char_handle].setEnabled(False)
                self.log.info("Char: {} Notification Actions Disabled".format(char))
                # self.chars_to_notify.remove(char)
                # self.chars_to_notify_handles.remove(char_handle)
            for char_handle in self.write_char_actions_dict:
                for action in self.write_char_actions_dict[char_handle]:
                    if action != 'set_value_box':
                        self.write_char_actions_dict[char_handle][action].setEnabled(False)
                    else:
                        self.write_char_actions_dict[char_handle][action].hide()
            self.device_status_action.setText('Status: Disconnected')
        elif data == 'disconnecting':
            self.device_status_action.setText('Status: Disconnecting...')
        elif isinstance(data, list):
            if data[0] == 'reconnect':
                self.device_status_action.setText('Status: Reconnection in {} s'.format(29 - data[1]))
        elif data == 'reconnecting':
            self.device_status_action.setText('Status: Reconnecting...')

        elif data == 'connected':
            if self.notify_status_is_on:
                self.notify("Reconnection event",
                            'Device {} is now connected'.format(self.esp32_device.name),
                            typeicon='Info')
            self.device_status_action.setText('Status: Connected')
            for char_handle in self.esp32_device.notifiables_handles:
                char = self.esp32_device.notifiables_handles[char_handle]
                if char_handle in self.chars_to_notify_handles:
                    self.main_server.send_message("start:{}:{}".format(char_handle, char))
                    time.sleep(1)
                self.notify_char_actions_dict[char_handle].setEnabled(True)
                self.log.info("Char: {} Notification Actions Enabled".format(char))
            for char_handle in self.write_char_actions_dict:
                for action in self.write_char_actions_dict[char_handle]:
                    if action != 'set_value_box':
                        self.write_char_actions_dict[char_handle][action].setEnabled(True)
        elif data == 'timeupdate':
            self.last_update_action.setText("Last Update: {}".format(datetime.strftime(datetime.now(), "%H:%M:%S")))

        else:
            if not data:
                pass
            else:
                try:
                    for char_handle in data.keys():
                        if isinstance(char_handle, int):
                            char = self.esp32_device.readables_handles[char_handle]
                            # HANDLE SINGLE VALUES
                            if len(self.esp32_device.chars_xml[char].fields) == 1:
                                # CHECK IF BITFIELD
                                _bfield = False
                                for field in self.esp32_device.chars_xml[char].fields:
                                    if 'BitField' in self.esp32_device.chars_xml[char].fields[field]:
                                        _bfield = True
                                if not _bfield:
                                    char_text = self.esp32_device.pformat_char_value(data[char_handle],
                                                                                     char=char,
                                                                                     rtn=True,
                                                                                     prnt=False,
                                                                                     one_line=True,
                                                                                     only_val=True)

                                    self.char_actions_dict[char_handle].setText(char_text)
                                    for serv in self.esp32_device.services_rsum.keys():
                                        if char in self.esp32_device.services_rsum[serv]:
                                            self.log.info("[{}] {}".format(serv, char_text))
                                    # SAVE FOR TOOLTIP
                                    for field in self.esp32_device.chars_xml[char].fields:
                                        self.tooltip_h_ch_field_values_dict[char_handle][char][field] = char_text
                                else:
                                    # HANDLE BITFLAGS
                                    bitflagdict = data[char_handle][char]['Value']
                                    for _bitfield in bitflagdict:
                                        bitfield_text = "{}: {}".format(_bitfield, bitflagdict[_bitfield])
                                        self.char_fields_actions_dict[char_handle][_bitfield].setText(bitfield_text)
                                        # SAVE FOR TOOLTIP
                                        self.tooltip_h_ch_field_values_dict[char_handle][char][_bitfield] = bitfield_text
                                        for serv in self.esp32_device.services_rsum.keys():
                                            if char in self.esp32_device.services_rsum[serv]:
                                                self.log.info("[{}] {} {}".format(serv, char, bitfield_text))

                            elif len(self.esp32_device.chars_xml[char].fields) > 1:
                                for field in self.esp32_device.chars_xml[char].fields:
                                    # NORMAL FIELD
                                    if field in data[char_handle]:
                                        if 'BitField' not in self.esp32_device.chars_xml[char].fields[field]:
                                            if "Reference" not in self.esp32_device.chars_xml[char].fields[field]:
                                                field_val = self.esp32_device.pformat_field_value(data[char_handle][field],
                                                                                                 rtn=True,
                                                                                                 prnt=False)
                                            else:
                                                # REFERENCE FIELD
                                                reference = self.esp32_device.chars_xml[char].fields[field]["Reference"]
                                                if reference in data[char_handle][field][reference]:
                                                    field_val = self.esp32_device.pformat_field_value(data[char_handle][field][reference][reference],
                                                                                                     rtn=True,
                                                                                                     prnt=False)
                                                elif field in data[char_handle][field][reference]:
                                                    field_val = self.esp32_device.pformat_field_value(data[char_handle][field][reference][field],
                                                                                                     rtn=True,
                                                                                                     prnt=False)
                                                else:
                                                    if reference == 'Date Time':
                                                        field_val = self.esp32_device.pformat_field_value(data[char_handle][field][reference],
                                                                                                             rtn=True,
                                                                                                             prnt=False,
                                                                                                             timestamp=True)
                                                    else:
                                                        field_val = self.esp32_device.pformat_ref_char_value(data[char_handle][field], rtn=True)
                                            field_text = "{}: {}".format(field, field_val)
                                            self.char_fields_actions_dict[char_handle][field].setText(field_text)
                                            # SAVE FOR TOOLTIP
                                            self.tooltip_h_ch_field_values_dict[char_handle][char][field] = field_text
                                            for serv in self.esp32_device.services_rsum.keys():
                                                if char in self.esp32_device.services_rsum[serv]:
                                                    self.log.info("[{}] {} {}".format(serv, char, field_text))
                                        else:
                                            # HANDLE BITFLAGS
                                            bitflagdict = data[char_handle][field]['Value']
                                            for _bitfield in bitflagdict:
                                                bitfield_text = "{}: {}".format(_bitfield, bitflagdict[_bitfield])
                                                self.char_fields_bitfields_actions_dict[char_handle][field][_bitfield].setText(bitfield_text)
                                                # SAVE FOR TOOLTIP
                                                self.tooltip_h_ch_field_values_dict[char_handle][char][_bitfield] = bitfield_text
                                                for serv in self.esp32_device.services_rsum.keys():
                                                    if char in self.esp32_device.services_rsum[serv]:
                                                        self.log.info("[{}] {} ({}) {}".format(serv, char, field, bitfield_text))
                    # SET TOOLTIP
                    if self.checklist_choices:
                        self.log.info("Tool Tip Fields: {}".format(self.checklist_choices))
                    self.format_tool_tip()
                    # LAST UPDATE
                    self.last_update_action.setText("Last Update: {}".format(datetime.strftime(datetime.now(), "%H:%M:%S")))
                    self.device_status_action.setText('Status: Connected')
                    if 'DEVICE_RSSI' in data:
                        self._rssi_buffer.pop(0)
                        self._rssi_buffer.append(data['DEVICE_RSSI'])
                        _av_rssi_val = int(sum(self._rssi_buffer)/len(self._rssi_buffer))
                        self.device_rssi_action.setText('RSSI: {} dBm'.format(_av_rssi_val))
                except Exception as e:
                    self.log.error(traceback.format_exc())

    def update_menu(self, progress_callback):  # define the notify callback inside that takes progress_callback as variable
        connect_loop = False
        qthread = threading.current_thread()
        qthread.name = 'BleDevThread'
        self.esp32_device.break_flag = self.quit_thread
        while not self.quit_thread:
            if self.quit_thread:
                break
            else:
                if not connect_loop:
                    self._timeout_count += 1
                    try:
                        if self._read_timeout == self._timeout_count:
                            data = {}
                            for char_handle in self.esp32_device.readables_handles.keys():
                                char = self.esp32_device.readables_handles[char_handle]
                                if char not in self.avoid_chars and char_handle not in self.chars_to_notify_handles:
                                    if self.quit_thread:
                                        break
                                    else:
                                        try:
                                            data[char_handle] = (self.esp32_device.get_char_value(char, handle=char_handle))
                                        except struct.error:
                                            self.log.error("Char: {}, Error: Wrong encoding format".format(char))
                                            data[char_handle] = {char: {"Value": " ", "Symbol":"?"}}
                            data['DEVICE_RSSI'] = self.esp32_device.get_RSSI()
                            progress_callback.emit(data)
                            self._timeout_count = 0
                        else:
                            if self.esp32_device.is_connected():
                                progress_callback.emit('timeupdate')
                            else:
                                raise DisconnectionError('Device {} disconnected'.format(self.esp32_device.name))
                    except (TypeError, DisconnectionError) as e:
                        self.log.error("Char: {}, Error: {}".format(char, e))
                        if self.esp32_device.is_connected():
                            self.log.info('Disconnecting...')
                            progress_callback.emit('disconnecting')
                            status = self.esp32_device.is_connected()
                            self.log.info('Connected: {}'.format(status))
                            if self.quit_thread:
                                break
                            while True:
                                if self.quit_thread:
                                    break
                                self.log.info('Assert Disconnection...')
                                try:
                                    self.esp32_device.disconnect(timeout=1)
                                    time.sleep(1)
                                    break
                                except Exception as e:
                                    self.log.error('Disconnection timeout')
                                    time.sleep(5)

                        else:
                            self.log.info("Device disconnected")
                            progress_callback.emit('disconnected')
                            self.esp32_device.connected = False
                            connect_loop = True
                            time.sleep(4)
                    except Exception as e:
                        self.log.error("Char: {}, Error: {}".format(char, traceback.format_exc()))
                        progress_callback.emit(False)
                        if self.esp32_device.is_connected():
                            self._timeout_count = 0
                        else:
                            self.log.info("Device disconnected")
                            progress_callback.emit('disconnected')
                            self.esp32_device.connected = False
                            connect_loop = True
                            time.sleep(4)
                else:
                    self._timeout_count = 0
                    self.log.info("Trying to reconnect...")
                    progress_callback.emit('reconnecting')
                    self.esp32_device.connect()
                    if self.esp32_device.connected:
                        self.log.info("Device reconnected...")
                        progress_callback.emit('connected')
                        connect_loop = False
                    else:
                        self.log.info("Device unreachable...")
                        self.log.info("Trying again in 30 seconds")
                        for i in range(29):
                            progress_callback.emit(['reconnect', i])
                            time.sleep(1)
                            if self.quit_thread:
                                break
                        if self.quit_thread:
                            break
            time.sleep(1)
        progress_callback.emit("finished")
        self.menu_thread_done = True
        self.log.info("FINISHED")

    def start_update_menu(self):
        # Pass the function to execute
        worker_menu = Worker(self.update_menu)  # Any other args, kwargs are passed to the run function
        # worker.signals.result.connect(self.print_output)
        # worker.signals.finished.connect(self.thread_complete)
        # worker.signals.progress.connect(self.progress_fn)
        worker_menu.signals.progress.connect(self.refresh_menu)

        # Execute
        self.threadpool.start(worker_menu)

    def receive_notification(self, response):

        data = response
        try:
            for char_handle in data.keys():
                char = self.esp32_device.notifiables_handles[char_handle]
                if char != 'Battery Power State':
                    try:
                        data_value = get_char_value(data[char_handle], self.esp32_device.chars_xml[char])
                    except struct.error:
                        self.log.error("Notification Char: {}, Error: Wrong encoding format".format(char))
                        data_value = {char: {"Value": " ", "Symbol":"?"}}
                    if len(self.esp32_device.chars_xml[char].fields) == 1:
                        # CHECK IF BITFIELD
                        _bfield = False
                        for field in self.esp32_device.chars_xml[char].fields:
                            if 'BitField' in self.esp32_device.chars_xml[char].fields[field]:
                                _bfield = True
                        if not _bfield:
                            data_value_string = pformat_char_value(data_value,
                                                                   rtn=True,
                                                                   prnt=False,
                                                                   one_line=True,
                                                                   only_val=True)
                            self.char_actions_dict[char_handle].setText(
                                "{}: {}".format(char, data_value_string))
                            # SAVE FOR TOOLTIP
                            for field in self.esp32_device.chars_xml[char].fields:
                                self.tooltip_h_ch_field_values_dict[char_handle][char][field] = "{}: {}".format(field, data_value_string)
                        else:
                            # HANDLE BITFLAGS
                            for field in self.esp32_device.chars_xml[char].fields:
                                bitflagdict = data_value[field]['Value']
                            data_value_string = '\n'.join(list(bitflagdict.values()))
                            for _bitfield in bitflagdict:
                                bitfield_text = "{}: {}".format(_bitfield, bitflagdict[_bitfield])
                                self.char_fields_actions_dict[char_handle][_bitfield].setText(bitfield_text)
                                # SAVE FOR TOOLTIP
                                self.tooltip_h_ch_field_values_dict[char_handle][char][_bitfield] = bitfield_text
                    else:
                        field_strings = []
                        for field in self.esp32_device.chars_xml[char].fields:
                            # NORMAL FIELD
                            if field in data_value:
                                if 'BitField' not in self.esp32_device.chars_xml[char].fields[field]:
                                    if "Reference" not in self.esp32_device.chars_xml[char].fields[field]:
                                        field_val = self.esp32_device.pformat_field_value(data_value[field],
                                                                                         rtn=True,
                                                                                         prnt=False)
                                    else:
                                        # REFERENCE FIELD
                                        reference = self.esp32_device.chars_xml[char].fields[field]["Reference"]
                                        if field in data_value[field][reference]:
                                            field_val = self.esp32_device.pformat_field_value(data_value[field][reference][field],
                                                                                             rtn=True,
                                                                                             prnt=False)
                                        else:
                                            if reference == 'Date Time':
                                                field_val = self.esp32_device.pformat_field_value(data_value[field][reference],
                                                                                                     rtn=True,
                                                                                                     prnt=False,
                                                                                                     timestamp=True)
                                            else:
                                                field_val = self.esp32_device.pformat_ref_char_value(data_value[field], rtn=True)

                                    field_text = "{}: {}".format(field, field_val)
                                    self.char_fields_actions_dict[char_handle][field].setText(field_text)
                                    # SAVE FOR TOOLTIP
                                    self.tooltip_h_ch_field_values_dict[char_handle][char][field] = field_text
                                    field_strings.append(field_val)
                                else:
                                    # HANDLE BITFLAGS
                                    bitflagdict = bitflagdict = data_value[field]['Value']
                                    for _bitfield in bitflagdict:
                                        field_strings.append(bitflagdict[_bitfield])
                                        bitfield_text = "{}: {}".format(_bitfield, bitflagdict[_bitfield])
                                        self.char_fields_bitfields_actions_dict[char_handle][field][_bitfield].setText(bitfield_text)
                                        # SAVE FOR TOOLTIP
                                        self.tooltip_h_ch_field_values_dict[char_handle][char][_bitfield] = bitfield_text

                        data_value_string = ', '.join(field_strings)

                    for serv in self.esp32_device.services_rsum.keys():
                        if char in self.esp32_device.services_rsum[serv]:
                            nservice = serv
                    if self.do_desktop_notify_char_dict[char_handle]:
                        self.notify("{}@{}:".format(self.esp32_device.name, nservice), "{} Is now: {}".format(
                            char, data_value_string))

                    for serv in self.esp32_device.services_rsum.keys():
                        if char in self.esp32_device.services_rsum[serv]:
                            self.log.info("Notification: [{}] {} : {}".format(serv, char, data_value_string))
                else:
                    try:
                        data_value = get_char_value(data[char_handle], self.esp32_device.chars_xml[char])
                    except struct.error:
                        self.log.error("Notification Char: {}, Error: Wrong encoding format".format(char))
                        data_value = {char: {"Value": " ", "Symbol":"?"}}
                    self.esp32_device.batt_power_state = self.esp32_device.map_powstate(data_value['State']['Value'])
                    for state, value in self.esp32_device.batt_power_state.items():
                        self.battery_power_state_actions_dict[state].setText("{}: {}".format(state, value))
                    for serv in self.esp32_device.services_rsum.keys():
                        if char in self.esp32_device.services_rsum[serv]:
                            nservice = serv
                    if self.do_desktop_notify_char_dict[char_handle]:
                        if self.esp32_device.batt_power_state['Level'] == 'Good Level':
                            self.notify("{}@{}:".format(self.esp32_device.name, nservice), "{} Is now: {} {}".format(char, self.esp32_device.batt_power_state['Charging State'],
                                                                                                              self.esp32_device.batt_power_state['Level']), typeicon='Info')
                        else:
                            self.notify("{}@{}:".format(self.esp32_device.name, nservice), "{} Is now: {} {}".format(char, self.esp32_device.batt_power_state['Charging State'],
                                                                                                              self.esp32_device.batt_power_state['Level']))

                    for serv in self.esp32_device.services_rsum.keys():
                        if char in self.esp32_device.services_rsum[serv]:
                            self.log.info("Notification: [{}] {} : {} {}".format(serv,
                                                                                 char, self.esp32_device.batt_power_state['Charging State'],
                                                                                 self.esp32_device.batt_power_state['Level']))
        except Exception as e:
            self.log.error(traceback.format_exc())

    def subscribe_notify(self, progress_callback):  # run in thread
        qthread = threading.current_thread()
        qthread.name = 'NotifyThread'

        def readnotify_callback(sender_handle, data, callb=progress_callback):

            # char = uuidstr_to_str(cb_uuid_to_str(sender_uuid))
            try:
                data_dict = {sender_handle: data}
                callb.emit(data_dict)
            except Exception as e:
                self.log.error(e)

        async def as_char_notify(notify_callback=readnotify_callback):
            aio_client_r, aio_client_w = await asyncio.open_connection('localhost', self.port)
            aio_client_w.write('started'.encode())
            for char_handle in self.chars_to_notify_handles:
                await self.esp32_device.ble_client.start_notify(char_handle, notify_callback)
                self.log.info('Started Notification on: {}'.format(self.esp32_device.notifiables_handles[char_handle]))
            await asyncio.sleep(1)
            while True:
                data = await aio_client_r.read(1024)
                message = data.decode()
                self.log.info('{}'.format(message))
                if message == 'exit':
                    aio_client_w.write('ok'.encode())
                    self.log.info('{}'.format("Stopping notifications now..."))
                    for char_handle in self.chars_to_notify_handles:
                        if hasattr(self.esp32_device.ble_client, 'stop_notify'):
                            await self.esp32_device.ble_client.stop_notify(char_handle)
                    aio_client_w.close()
                    self.log.info('{}'.format("Done!"))
                    self.char_to_notify = None
                    break
                else:
                    action, char_handle_str, char = message.split(':')
                    char_handle = int(char_handle_str)
                    # char = self.esp32_device.notifiables_handles[char_handle]
                    if action == 'start':
                        await self.esp32_device.ble_client.start_notify(char_handle, notify_callback)
                        self.log.info('Started Notification on: {}'.format(char))
                    if action == 'stop':
                        await self.esp32_device.ble_client.stop_notify(char_handle)
                        self.log.info('Stopped Notification on: {}'.format(char))
                    await asyncio.sleep(1)

        # GET NEW EVENT LOOP AND RUN
        try:
            asyncio.set_event_loop(self.notify_loop)
            self.notify_loop.run_until_complete(as_char_notify())

        except Exception as e:
            self.log.error('{}'.format(e))
        self.log.info('{}'.format("FINISHED"))
        self.notify_thread_done = True

    def start_notify_char(self):
        self.notify_thread_done = False
        # Pass the function to execute
        worker_notify = Worker(self.subscribe_notify)  # Any other args, kwargs are passed to the run function
        # worker.signals.result.connect(self.print_output)
        # worker.signals.finished.connect(self.thread_complete)
        # worker.signals.progress.connect(self.progress_fn)
        worker_notify.signals.progress.connect(self.receive_notification)

        # Execute
        self.main_server = socket_server(8845, log=self.log)
        self.port = self.main_server.get_free_port()  # start stop multiple chars to notify
        self.threadpool.start(worker_notify)
        self.main_server.start_SOC()
        self.log.info("[NotifyThread] {}".format(self.main_server.recv_message()))

    def notify(self, typemessage, message, typeicon='Warning'):
        """Generate a desktop notification"""
        if self.notify_sound_is_on:
            self.notify_sound.play()
        self.showMessage(typemessage,
                         message,
                         self.notify_type_icon[typeicon],
                         60*60000)

    def show_checklist_dialog(self):
        self.set_tool_tip_dialog.show()
        self.set_tool_tip_dialog.raise_()

    def format_tool_tip(self):
        tooltip_string_list = []
        for fld in self.checklist_choices:
            _char, _field, _handle = *fld.split(':')[:-1], int(fld.split(':')[-1])
            _field_value_string = self.tooltip_h_ch_field_values_dict[_handle][_char][_field]
            for string_to_avoid in self.avoid_field_strings:
                if string_to_avoid in _field_value_string:
                    _field_value_string = _field_value_string.replace(string_to_avoid, '')
            tooltip_string_list.append(_field_value_string)
        if tooltip_string_list:
            tool_tip_text = '\n'.join(tooltip_string_list)
            self.setToolTip(tool_tip_text)
        else:
            self.setToolTip('')

    def about_url(self):
        url = QUrl('https://github.com/Carglglz/bleico')
        QDesktopServices.openUrl(url)

    def show_console(self):
        self.console_logger.widget.show()

    def shutdown(self, loop):
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

        self.log.info("ASYNCIO EVENT LOOP: SHUTDOWN COMPLETE")

    def stop_notify_thread(self):

        # REINITIATE THREADS

        try:

            self.main_server.send_message('exit')
            self.main_server.recv_message()
            self.main_server.serv_soc.close()
        except Exception as e:
            self.log.error(e)

    def exit_app(self):
        # self.log.removeHandler(self.console_logger)

        self.log.info('Closing now...')
        self.log.info('Done!')
        self.log.info('Shutdown pending tasks...')
        try:
            self.quit_thread = True
            self.esp32_device.break_flag = self.quit_thread
            if self.main_server:
                self.main_server.send_message('exit')
                self.main_server.recv_message()
                self.main_server.serv_soc.close()
            else:
                time.sleep(0.5)
        except Exception as e:
            self.quit_thread = True
            self.log.error(e)
        while not self.notify_thread_done:
            self.log.info("Waiting for NotifyThread")
            time.sleep(0.5)
        try:
            while not self.menu_thread_done:
                self.log.info("Waiting for BleDevThread")
                time.sleep(0.5)
            if self.esp32_device.connected:
                self.log.info("Disconnecting Device...")
                self.esp32_device.disconnect()
        except Exception as e:
            pass

        loop_is_running = self.esp32_device.loop.is_running()
        self.log.info("LOOP IS RUNNING : {}".format(loop_is_running))
        if loop_is_running:
            self.shutdown(self.esp32_device.loop)
        # Run loop until tasks done

        try:
            while not self.menu_thread_done:
                self.log.info("Waiting for BleDevThread")
                time.sleep(0.5)
            if self.esp32_device.connected:
                self.log.info("Disconnecting Device...")
                self.esp32_device.disconnect()
        except Exception as e:
            pass
        self.log.info("SHUTDOWN COMPLETE")
        sys.exit()
