#!/usr/bin/env python3
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
desc_string = """Characteristic Aggregate Format      org.bluetooth.descriptor.gatt.characteristic_aggregate_format      0x2905      GSS
Characteristic Extended Properties      org.bluetooth.descriptor.gatt.characteristic_extended_properties      0x2900      GSS
Characteristic Presentation Format      org.bluetooth.descriptor.gatt.characteristic_presentation_format      0x2904      GSS
Characteristic User Description      org.bluetooth.descriptor.gatt.characteristic_user_description      0x2901      GSS
Client Characteristic Configuration      org.bluetooth.descriptor.gatt.client_characteristic_configuration      0x2902      GSS
Environmental Sensing Configuration      org.bluetooth.descriptor.es_configuration      0x290B      GSS
Environmental Sensing Measurement      org.bluetooth.descriptor.es_measurement      0x290C      GSS
Environmental Sensing Trigger Setting      org.bluetooth.descriptor.es_trigger_setting      0x290D      GSS
External Report Reference      org.bluetooth.descriptor.external_report_reference      0x2907      GSS
Number of Digitals      org.bluetooth.descriptor.number_of_digitals      0x2909      GSS
Report Reference      org.bluetooth.descriptor.report_reference      0x2908      GSS
Server Characteristic Configuration      org.bluetooth.descriptor.gatt.server_characteristic_configuration      0x2903      GSS
Time Trigger Setting      org.bluetooth.descriptor.time_trigger_setting      0x290E      GSS
Valid Range      org.bluetooth.descriptor.valid_range      0x2906      GSS
Value Trigger Setting      org.bluetooth.descriptor.value_trigger_setting      0x290A      GSS"""


desclist = desc_string.splitlines()
ble_descriptors_dict = {l.split()[-2].replace('0x', ''): l.split('org.')[0].strip() for l in desclist}
ble_descriptors_dict_rev = {v: k for k, v in ble_descriptors_dict.items()}
