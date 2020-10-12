#!/usr/bin/env python3
# @Author: carlosgilgonzalez
# @Date:   2020-07-12T15:41:44+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2020-08-06T20:55:36+01:00

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


import ast
from bleak_sigspec.formatter import SuperStruct
from bleak_sigspec.utils import get_xml_char, _autoformat_reqs, _get_req
from PyQt5.QtWidgets import (QWidget, QPushButton,
                             QComboBox, QVBoxLayout, QLabel, QLineEdit,
                             QDateTimeEdit, QScrollArea)
from PyQt5.QtCore import Qt, QDate

struct = SuperStruct()


class SetValueDialog(QWidget):
    def __init__(self, char=None, char_handle=None, log=None, dev=None):
        super().__init__()
        self.char = char
        self.char_fields = char.fields.copy()
        self.char_handle = char_handle
        self.layout = QVBoxLayout()
        self.label_fields = {}
        self.label_char = {}
        self.line_fields = {}
        self.line_char = {}
        self.combo_fields = {}
        self.label_flag_fields = {}
        self.combo_flag_fields = {}
        self.format_fields = {}
        self.value_fields = {}
        self.global_format = ""
        self.global_flag = ''
        self.flag_format = "B"
        self._datetime_chars = ['Date Time']
        self._date_chars = ['Date of Birth', 'Date of Threshold Assessment']
        self.fields_to_pop = []
        self.opt_ref_fields = {}
        self._flag_reqs = {}
        self.log = log
        self.dev = dev
        # SCROLL AREA
        self.scroll_layout = QVBoxLayout()
        self.scrollArea = QScrollArea()
        self.top_widget = QWidget()

        # GET REFERENCES
        for field in self.char_fields.copy():
            if 'Reference' in self.char_fields[field]:
                if 'Requirement' in self.char_fields[field]:
                    if self.char_fields[field]['Requirement'] == 'Mandatory':
                        ref_char = get_xml_char(self.char_fields[field]['Reference'])
                        print(field, ref_char.name)
                        if ref_char.name not in self._datetime_chars and ref_char.name not in self._date_chars:
                            if len(ref_char.fields) == 1:
                                for ref_field in ref_char.fields:
                                    self.char_fields[field] = ref_char.fields[ref_field]
                            else:
                                self.char_fields.pop(field)
                                # self.fields_to_pop.append(field)
                                for ref_field in ref_char.fields:
                                    self.char_fields[ref_field] = ref_char.fields[ref_field]
                        else:
                            self.opt_ref_fields[ref_char.name] = {}
                            if len(ref_char.fields) == 1:
                                for ref_field in ref_char.fields:
                                    self.opt_ref_fields[ref_char.name][field] = ref_char.fields[ref_field]
                            else:

                                for ref_field in ref_char.fields:
                                    self.opt_ref_fields[ref_char.name][ref_field] = ref_char.fields[ref_field]

                    else:
                        ref_char = get_xml_char(self.char_fields[field]['Reference'])
                        self.opt_ref_fields[ref_char.name] = {}
                        if len(ref_char.fields) == 1:
                            for ref_field in ref_char.fields:
                                self.opt_ref_fields[ref_char.name][field] = ref_char.fields[ref_field]
                        else:

                            for ref_field in ref_char.fields:
                                self.opt_ref_fields[ref_char.name][ref_field] = ref_char.fields[ref_field]

                else:
                    ref_char = get_xml_char(self.char_fields[field]['Reference'])
                    if len(ref_char.fields) == 1:
                        for ref_field in ref_char.fields:
                            self.char_fields[field] = ref_char.fields[ref_field]
                    else:
                        self.char_fields.pop(field)
                        # self.fields_to_pop.append(field)
                        for ref_field in ref_char.fields:
                            self.char_fields[ref_field] = ref_char.fields[ref_field]

        # FIELD LABELS
        if self.char.name in self._datetime_chars or self.char.name in self._date_chars:
            self.label_char[self.char.name] = QLabel("{}".format(self.char.name))
            for field in self.char_fields:
                if 'Ctype' in self.char_fields[field]:
                    self.format_fields[field] = self.char_fields[field]['Ctype']
            self.line_char[self.char.name] = QDateTimeEdit(QDate.currentDate())
            if self.char.name in self._date_chars:
                self.line_char[self.char.name].setDisplayFormat("yyyy-MM-dd")
            else:
                self.line_char[self.char.name].setDisplayFormat("yyyy-MM-dd hh:mm:ss")
            self.layout.addWidget(self.label_char[self.char.name])
            self.layout.addWidget(self.line_char[self.char.name])
        else:

            for field in self.char_fields:
                if field != 'Flags':
                    if 'Unit' in self.char_fields[field] and self.char_fields[field]['Unit'] != 'unitless':
                        self.label_fields[field] = QLabel("{} ({})".format(field,
                                                                           self.char_fields[field]['Symbol']))
                    else:
                        self.label_fields[field] = QLabel(field)
                    if 'Ctype' in self.char_fields[field]:
                        self.format_fields[field] = self.char_fields[field]['Ctype']
                    self.label_fields[field].setAlignment(Qt.AlignLeft)
                    if 'Unit' in self.char_fields[field]:
                        self.line_fields[field] = QLineEdit()
                        self.layout.addWidget(self.label_fields[field])
                        self.layout.addWidget(self.line_fields[field])
                    elif 'Enumerations' in self.char_fields[field] and 'BitField' not in self.char_fields[field]:
                        if len(list(self.char_fields[field]['Enumerations'].values())) == 1:
                            self.label_fields[field] = QLabel("{}".format(field))
                            self.line_fields[field] = QLineEdit()
                            self.layout.addWidget(self.label_fields[field])
                            self.layout.addWidget(self.line_fields[field])

                        else:
                            self.combo_fields[field] = QComboBox()
                            self.combo_fields[field].addItems(list(self.char_fields[field]['Enumerations'].values()))
                            self.layout.addWidget(self.label_fields[field])
                            self.layout.addWidget(self.combo_fields[field])
                    elif 'BitField' in self.char_fields[field]:
                        for flag in self.char_fields[field]['BitField']:
                            self.label_flag_fields[flag] = QLabel(flag)
                            self.combo_flag_fields[flag] = QComboBox()
                            _flags = list(self.char_fields[field]['BitField'][flag]['Enumerations'].values())
                            _flag_list = [fl for fl in _flags if isinstance(fl, str)]
                            self.combo_flag_fields[flag].addItems(_flag_list)
                            self.layout.addWidget(self.label_flag_fields[flag])
                            self.layout.addWidget(self.combo_flag_fields[flag])

                    elif 'Reference' in self.char_fields[field]:
                        ref_char = self.char_fields[field]['Reference']
                        if ref_char in self.opt_ref_fields:
                            if ref_char not in self._date_chars and ref_char not in self._datetime_chars:
                                if len(self.opt_ref_fields[ref_char]) == 1:
                                    if 'Unit' in self.opt_ref_fields[ref_char][field]:
                                        self.label_fields[field].setText('{} {}'.format(ref_char, self.opt_ref_fields[ref_char][field]['Symbol']))
                                        self.line_fields[field] = QLineEdit()
                                        self.layout.addWidget(self.label_fields[field])
                                        self.layout.addWidget(self.line_fields[field])

                                    elif 'Enumerations' in self.opt_ref_fields[ref_char][field] and 'BitField' not in self.opt_ref_fields[ref_char][field]:
                                        if len(list(self.opt_ref_fields[ref_char][field]['Enumerations'].values())) == 1:
                                            self.label_fields[field] = QLabel("{}".format(field))
                                            self.line_fields[field] = QLineEdit()
                                            self.layout.addWidget(self.label_fields[field])
                                            self.layout.addWidget(self.line_fields[field])

                                        else:
                                            self.combo_fields[field] = QComboBox()
                                            self.combo_fields[field].addItems(list(self.opt_ref_fields[ref_char][field]['Enumerations'].values()))
                                            self.layout.addWidget(self.label_fields[field])
                                            self.layout.addWidget(self.combo_fields[field])

                                    if 'Ctype' in self.opt_ref_fields[ref_char][field]:
                                        self.format_fields[field] = self.opt_ref_fields[ref_char][field]['Ctype']

                                else:
                                    _ref_fields = ','.join([fld for fld in self.opt_ref_fields[ref_char]])
                                    self.label_fields[field].setText('{}: {} [{}]'.format(field, ref_char, _ref_fields))
                                    self.line_fields[field] = QLineEdit()
                                    self.layout.addWidget(self.label_fields[field])
                                    self.layout.addWidget(self.line_fields[field])
                                    for sf in self.opt_ref_fields[ref_char]:
                                        if 'Ctype' in self.opt_ref_fields[ref_char][sf]:
                                            self.format_fields[sf] = self.opt_ref_fields[ref_char][sf]['Ctype']
                            else:
                                self.label_char[field] = QLabel("{}".format(field))
                                for sf in self.opt_ref_fields[ref_char]:
                                    if 'Ctype' in self.opt_ref_fields[ref_char][sf]:
                                        self.format_fields[sf] = self.opt_ref_fields[ref_char][sf]['Ctype']
                                self.line_char[field] = QDateTimeEdit(QDate.currentDate())
                                if ref_char in self._date_chars:
                                    self.line_char[field].setDisplayFormat("yyyy-MM-dd")
                                else:
                                    self.line_char[field].setDisplayFormat("yyyy-MM-dd hh:mm:ss")
                                self.layout.addWidget(self.label_char[field])
                                self.layout.addWidget(self.line_char[field])
                    else:
                        self.label_fields[field] = QLabel("{}".format(field))
                        self.line_fields[field] = QLineEdit()
                        self.layout.addWidget(self.label_fields[field])
                        self.layout.addWidget(self.line_fields[field])
                else:
                    self.label_fields[field] = QLabel(field)
                    self.format_fields[field] = self.char_fields[field]['Ctype']
                    self.flag_format = self.char_fields[field]['Ctype']
                    self.layout.addWidget(self.label_fields[field])
                    if 'BitField' in self.char_fields[field]:
                        for flag in self.char_fields[field]['BitField']:
                            self.label_flag_fields[flag] = QLabel(flag)
                            self.combo_flag_fields[flag] = QComboBox()
                            _flags = list(self.char_fields[field]['BitField'][flag]['Enumerations'].values())
                            _flag_list = [fl for fl in _flags if isinstance(fl, str)]
                            self.combo_flag_fields[flag].addItems(_flag_list)
                            self.layout.addWidget(self.label_flag_fields[flag])
                            self.layout.addWidget(self.combo_flag_fields[flag])

        # Create a button in the window
        self.button_config = QPushButton('Set')
        self.button_config.move(20, 80)
        self.button_config.clicked.connect(self.on_push)
        self.top_widget.setLayout(self.layout)
        self.scrollArea.setWidget(self.top_widget)
        self.scrollArea.setWidgetResizable(True)
        # self.scrollArea.setFixedHeight(400)
        self.scroll_layout.addWidget(self.scrollArea)
        self.scroll_layout.addWidget(self.button_config)
        self.setLayout(self.scroll_layout)
        self.setWindowTitle("Set {} Value".format(self.char.name))

    def on_push(self):
        self.log.info('Setting {} Value to:'.format(self.char.name))
        self.global_format = ""
        self.global_flag = ''
        self.value_fields = {}
        if self.char.name not in self._date_chars and self.char.name not in self._datetime_chars:
            for field in self.char_fields:
                if field in self.line_fields:
                    text = self.line_fields[field].text()
                    # MANDATORY FIELDS
                    if self.char_fields[field]['Requirement'] == 'Mandatory':
                        if text == '':
                            text = '0'
                        try:
                            formatted_value = ast.literal_eval(text)
                        except Exception as e:
                            formatted_value = text

                        if 'Reference' in self.char_fields[field]:
                            ref_index = 0
                            ref_char = self.char_fields[field]['Reference']
                            if isinstance(formatted_value, list):
                                for _ref_field in self.opt_ref_fields[ref_char]:
                                    self.value_fields[_ref_field] = formatted_value[ref_index]
                                    self.global_format += self.format_fields[_ref_field]
                                    ref_index += 1
                            else:
                                for _ref_field in self.opt_ref_fields[ref_char]:
                                    self.value_fields[_ref_field] = formatted_value
                                    self.global_format += self.format_fields[_ref_field]
                            self.log.info('Value: {} {}'.format(ref_char, text))
                        else:
                            if "Multiplier" in self.char_fields[field]:
                                formatted_value *= (1/self.char_fields[field]["Multiplier"])
                            if "DecimalExponent" in self.char_fields[field]:
                                formatted_value /= (10 ** (self.char_fields[field]["DecimalExponent"]))
                            if "BinaryExponent" in self.char_fields[field]:
                                formatted_value *= (1 / 2 ** (self.char_fields[field]["BinaryExponent"]))

                            # encoded_value = struct.pack(self.format_fields[field], int(formatted_value))
                            # FIXME: assert correct format int/float/string ? max/min ?
                            if self.format_fields[field] == 'F' or self.format_fields[field] == 'S':
                                self.value_fields[field] = formatted_value
                            else:
                                try:
                                    self.value_fields[field] = int(formatted_value)
                                except Exception as e:
                                    self.value_fields[field] = formatted_value
                            self.global_format += self.format_fields[field]
                            if 'Symbol' in self.char_fields[field]:
                                self.log.info('Value: {} {}'.format(text, self.char_fields[field]['Symbol']))
                            else:
                                self.log.info('Value: {}'.format(text))
                    else:
                        # REQUIRED FIELDS
                        if self._flag_reqs:
                            field_req = _get_req(self.char_fields[field])
                            _WRITE_FIELD = all([req in self._flag_reqs.values() for req in field_req])
                            if _WRITE_FIELD:
                                if text == '':
                                    text = '0'
                                formatted_value = ast.literal_eval(text)

                                if 'Reference' in self.char_fields[field]:
                                    ref_index = 0
                                    ref_char = self.char_fields[field]['Reference']
                                    if isinstance(formatted_value, list):
                                        for _ref_field in self.opt_ref_fields[ref_char]:
                                            self.value_fields[_ref_field] = formatted_value[ref_index]
                                            self.global_format += self.format_fields[_ref_field]
                                            ref_index += 1
                                    else:
                                        for _ref_field in self.opt_ref_fields[ref_char]:
                                            self.value_fields[_ref_field] = formatted_value
                                            self.global_format += self.format_fields[_ref_field]
                                    self.log.info('Value: {} {}'.format(ref_char, text))
                                else:
                                    if "Multiplier" in self.char_fields[field]:
                                        formatted_value *= (1/self.char_fields[field]["Multiplier"])
                                    if "DecimalExponent" in self.char_fields[field]:
                                        formatted_value /= (10 ** (self.char_fields[field]["DecimalExponent"]))
                                    if "BinaryExponent" in self.char_fields[field]:
                                        formatted_value *= (1 / 2 ** (self.char_fields[field]["BinaryExponent"]))

                                    # encoded_value = struct.pack(self.format_fields[field], int(formatted_value))
                                    # FIXME: assert correct format int/float/string ? max/min ?
                                    if self.format_fields[field] == 'F' or self.format_fields[field] == 'S':
                                        self.value_fields[field] = formatted_value
                                    else:
                                        self.value_fields[field] = int(formatted_value)
                                    self.global_format += self.format_fields[field]
                                    if 'Symbol' in self.char_fields[field]:
                                        self.log.info('Value: {} {}'.format(text, self.char_fields[field]['Symbol']))
                                    else:
                                        self.log.info('Value: {}'.format(text))

                elif field in self.combo_fields:
                    # MANDATORY / REQUIRED ?
                    if self._flag_reqs:
                        field_req = _get_req(self.char_fields[field])
                        _WRITE_FIELD = all([req in self._flag_reqs.values() for req in field_req])
                        if _WRITE_FIELD:
                            text = self.combo_fields[field].currentText()
                            if 'Reference' in self.char_fields[field]:
                                ref_char = self.char_fields[field]['Reference']
                                if ref_char in self.opt_ref_fields:
                                    map_write_values = {v: int(k) for k, v in self.opt_ref_fields[ref_char][field]['Enumerations'].items()}
                            else:
                                map_write_values = {v: int(k) for k, v in self.char_fields[field]['Enumerations'].items()}
                            # encoded_value = struct.pack(self.format_fields[field], int(map_write_values[text]))
                            self.value_fields[field] = int(map_write_values[text])
                            self.global_format += self.format_fields[field]
                            self.log.info('Value: {} {}'.format(int(map_write_values[text]),
                                                                           text))

                    else:
                        text = self.combo_fields[field].currentText()
                        map_write_values = {v: int(k) for k, v in self.char_fields[field]['Enumerations'].items()}
                        # encoded_value = struct.pack(self.format_fields[field], int(map_write_values[text]))
                        self.value_fields[field] = int(map_write_values[text])
                        self.global_format += self.format_fields[field]
                        self.log.info('Value: {} {}'.format(int(map_write_values[text]),
                                                                       text))
                elif field == 'Flags':
                    self.global_flag = ''
                    if 'BitField' in self.char_fields[field]:
                        self.flag_format = self.char_fields[field]['Ctype']
                        for flag in self.char_fields[field]['BitField']:
                            text = self.combo_flag_fields[flag].currentText()
                            flag_map = self.char_fields[field]['BitField'][flag]['Enumerations'].items()
                            map_write_values = {v: int(k) for k, v in flag_map if isinstance(v, str)}
                            bitval = bin(map_write_values[text]).replace('0b', '')
                            bitfield_size = int(self.char_fields[field]['BitField'][flag]['size'])
                            # LEFT ZERO PADDING
                            while bitfield_size > len(bitval):
                                bitval = '0' + bitval
                            self.global_flag = bitval + self.global_flag
                        # RIGHT ZERO PADDING
                        while len(self.global_flag) < (struct.calcsize(self.flag_format) * 8):
                            self.global_flag = '0' + self.global_flag
                        self.global_flag = '0b' + self.global_flag
                        self.value_fields[field] = eval(self.global_flag)
                        self.global_format += self.format_fields[field]
                        self.log.info('Value: {} ({})'.format(field, self.global_flag))
                        # SET REQUIREMENTS
                        reqs = _autoformat_reqs(self.char, eval(self.global_flag))
                        self._flag_reqs = reqs['Flags']

                elif field != 'Flags' and 'BitField' in self.char_fields[field]:
                    self.global_flag = ''
                    if self._flag_reqs:
                        field_req = _get_req(self.char_fields[field])
                        _WRITE_FIELD = all([req in self._flag_reqs.values() for req in field_req])
                        if _WRITE_FIELD:
                            self.flag_format = self.char_fields[field]['Ctype']
                            for flag in self.char_fields[field]['BitField']:
                                text = self.combo_flag_fields[flag].currentText()
                                flag_map = self.char_fields[field]['BitField'][flag]['Enumerations'].items()
                                map_write_values = {v: int(k) for k, v in flag_map if isinstance(v, str)}
                                bitval = bin(map_write_values[text]).replace('0b', '')
                                bitfield_size = int(self.char_fields[field]['BitField'][flag]['size'])
                                # LEFT ZERO PADDING
                                while bitfield_size > len(bitval):
                                    bitval = '0' + bitval
                                self.global_flag = bitval + self.global_flag
                            # RIGHT ZERO PADDING
                            while len(self.global_flag) < (struct.calcsize(self.flag_format) * 8):
                                self.global_flag = '0' + self.global_flag
                            self.global_flag = '0b' + self.global_flag
                            self.value_fields[field] = eval(self.global_flag)
                            self.global_format += self.format_fields[field]
                            self.log.info('Value: {} ({})'.format(field, self.global_flag))
                    else:
                        self.flag_format = self.char_fields[field]['Ctype']
                        for flag in self.char_fields[field]['BitField']:
                            text = self.combo_flag_fields[flag].currentText()
                            flag_map = self.char_fields[field]['BitField'][flag]['Enumerations'].items()
                            map_write_values = {v: int(k) for k, v in flag_map if isinstance(v, str)}
                            bitval = bin(map_write_values[text]).replace('0b', '')
                            bitfield_size = int(self.char_fields[field]['BitField'][flag]['size'])
                            # LEFT ZERO PADDING
                            while bitfield_size > len(bitval):
                                bitval = '0' + bitval
                            self.global_flag = bitval + self.global_flag
                        # RIGHT ZERO PADDING
                        while len(self.global_flag) < (struct.calcsize(self.flag_format) * 8):
                            self.global_flag = '0' + self.global_flag
                        self.global_flag = '0b' + self.global_flag
                        self.value_fields[field] = eval(self.global_flag)
                        self.global_format += self.format_fields[field]
                        self.log.info('Value: {} ({})'.format(field, self.global_flag))

                elif field in self.line_char:
                    # DATE/ DATETIME
                    # MANDATORY
                    if self.char_fields[field]['Requirement'] == 'Mandatory':
                        if 'Reference' in self.char_fields[field]:
                            ref_char = self.char_fields[field]['Reference']
                        _datetime_ = self.line_char[field].dateTime().toPyDateTime()
                        _datetime_list = [_datetime_.year,
                                          _datetime_.month,
                                          _datetime_.day, _datetime_.hour,
                                          _datetime_.minute, _datetime_.second]
                        if ref_char in self._date_chars:
                            _datetime_list = _datetime_list[:3]

                        for sf in self.opt_ref_fields[ref_char]:
                            self.value_fields[sf] = _datetime_list.pop(0)
                            self.global_format += self.format_fields[sf]
                        self.log.info('Value: {} '.format(_datetime_.strftime('%Y-%m-%d %H:%M:%S')))
                    # REQUIRED
                    else:
                        if self._flag_reqs:
                            field_req = _get_req(self.char_fields[field])
                            _WRITE_FIELD = all([req in self._flag_reqs.values() for req in field_req])
                            if _WRITE_FIELD:
                                if 'Reference' in self.char_fields[field]:
                                    ref_char = self.char_fields[field]['Reference']
                                _datetime_ = self.line_char[field].dateTime().toPyDateTime()
                                _datetime_list = [_datetime_.year,
                                                  _datetime_.month,
                                                  _datetime_.day, _datetime_.hour,
                                                  _datetime_.minute, _datetime_.second]
                                if ref_char in self._date_chars:
                                    _datetime_list = _datetime_list[:3]

                                for sf in self.opt_ref_fields[ref_char]:
                                    self.value_fields[sf] = _datetime_list.pop(0)
                                    self.global_format += self.format_fields[sf]
                                self.log.info('Value: {} '.format(_datetime_.strftime('%Y-%m-%d %H:%M:%S')))

        else:
            _datetime_ = self.line_char[self.char.name].dateTime().toPyDateTime()
            _datetime_list = [_datetime_.year,
                              _datetime_.month,
                              _datetime_.day, _datetime_.hour,
                              _datetime_.minute, _datetime_.second]
            if self.char.name in self._date_chars:
                _datetime_list = _datetime_list[:3]

            for field in self.char_fields:
                self.value_fields[field] = _datetime_list.pop(0)
                self.global_format += self.format_fields[field]

            self.log.info('Value: {} '.format(_datetime_.strftime('%Y-%m-%d %H:%M:%S')))


        # self.log.info('Final Values: {}'.format(tuple(self.value_fields.values())))
        # self.log.info('Bytes: {}'.format(final_encoded_value))
        try:
            if self.value_fields:
                final_encoded_value = struct.pack(
                    self.global_format, *tuple(self.value_fields.values()))
                self.dev.write_char(self.char.name,
                                    data=final_encoded_value,
                                    handle=self.char_handle)
        except Exception as e:
            self.log.error(e)
        self.hide()
