from pyicloud import PyiCloudService as pis

import os

from time import sleep


user_name = os.environ.get('USER_NAME')
password = os.environ.get('PASSWORD')

api = pis(user_name, password)

for i, device in enumerate(api.devices):
    print(f"{i + 1}. {device}")

lat_lon = api.devices[1].location()

print(lat_lon)
