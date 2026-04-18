import usb
import sys
all_devs = usb.core.find(find_all=True)
for d in all_devs:
    print(d)
