import bluetooth
from ble_temp_amb import BLE_Battery_Temp


ble = bluetooth.BLE()
ble_temp_batt = BLE_Battery_Temp(ble)
