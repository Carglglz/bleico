#!/usr/bin/env python3
# @Author: carlosgilgonzalez
# @Date:   2020-07-12T15:41:44+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2020-08-06T17:18:31+01:00

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
import struct
from bleak.utils import get_xml_char
from PyQt5.QtWidgets import (QWidget, QPushButton,
                             QComboBox, QVBoxLayout, QLabel, QLineEdit)
from PyQt5.QtCore import Qt


class SetValueDialog(QWidget):
    def __init__(self, char=None, char_handle=None, log=None, dev=None):
        super().__init__()
        self.char = char
        self.char_fields = char.fields.copy()
        self.char_handle = char_handle
        self.layout = QVBoxLayout()
        self.label_fields = {}
        self.line_fields = {}
        self.combo_fields = {}
        self.label_flag_fields = {}
        self.combo_flag_fields = {}
        self.format_fields = {}
        self.value_fields = {}
        self.global_format = ""
        self.global_flag = ''
        self.flag_format = "B"
        self.fields_to_pop = []
        self.opt_ref_fields = {}
        self.log = log
        self.dev = dev

        # GET REFERENCES
        for field in self.char_fields.copy():
            if 'Reference' in self.char_fields[field]:
                if 'Requirement' in self.char_fields[field]:
                    if self.char_fields[field]['Requirement'] == 'Mandatory':
                        ref_char = get_xml_char(self.char_fields[field]['Reference'])
                        if len(ref_char.fields) == 1:
                            for ref_field in ref_char.fields:
                                self.char_fields[field] = ref_char.fields[ref_field]
                        else:
                            self.char_fields.pop(field)
                            # self.fields_to_pop.append(field)
                            for ref_field in ref_char.fields:
                                self.char_fields[ref_field] = ref_char.fields[ref_field]
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
                elif 'Enumerations' in self.char_fields[field]:
                    self.combo_fields[field] = QComboBox()
                    self.combo_fields[field].addItems(list(self.char_fields[field]['Enumerations'].values()))
                    self.layout.addWidget(self.label_fields[field])
                    self.layout.addWidget(self.combo_fields[field])
                elif 'Reference' in self.char_fields[field]:
                    ref_char = self.char_fields[field]['Reference']
                    if ref_char in self.opt_ref_fields:
                        _ref_fields = ','.join([fld for fld in self.opt_ref_fields[ref_char]])
                        self.label_fields[field].setText('{}: {} [{}]'.format(field, ref_char, _ref_fields))
                        self.line_fields[field] = QLineEdit()
                        self.layout.addWidget(self.label_fields[field])
                        self.layout.addWidget(self.line_fields[field])
                        for sf in self.opt_ref_fields[ref_char]:
                            if 'Ctype' in self.opt_ref_fields[ref_char][sf]:
                                self.format_fields[sf] = self.opt_ref_fields[ref_char][sf]['Ctype']
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
        self.layout.addWidget(self.button_config)

        self.setLayout(self.layout)
        self.setWindowTitle("Set {} Value".format(self.char.name))

    def on_push(self):
        self.log.info('Setting {} Value to:'.format(self.char.name))
        self.global_format = ""
        self.global_flag = ''
        self.value_fields = {}
        for field in self.char_fields:
            if field in self.line_fields:
                text = self.line_fields[field].text()
                if self.char_fields[field]['Requirement'] == 'Mandatory' or text != '' :
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
                        self.value_fields[field] = int(formatted_value)
                        self.global_format += self.format_fields[field]
                        self.log.info('Value: {} {}'.format(text, self.char_fields[field]['Symbol']))
            elif field in self.combo_fields:
                text = self.combo_fields[field].currentText()
                map_write_values = {v: int(k) for k, v in self.char_fields[field]['Enumerations'].items()}
                # encoded_value = struct.pack(self.format_fields[field], int(map_write_values[text]))
                self.value_fields[field] = int(map_write_values[text])
                self.global_format += self.format_fields[field]
                self.log.info('Value: {} {}'.format(int(map_write_values[text]),
                                                               text))
            elif field == 'Flags':
                if 'BitField' in self.char_fields[field]:
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

        final_encoded_value = struct.pack(self.global_format, *tuple(self.value_fields.values()))
        # self.log.info('Final Values: {}'.format(tuple(self.value_fields.values())))
        # self.log.info('Bytes: {}'.format(final_encoded_value))
        try:

            self.dev.write_char(self.char.name,
                                data=final_encoded_value,
                                handle=self.char_handle)
        except Exception as e:
            self.log.error(e)
        self.hide()
