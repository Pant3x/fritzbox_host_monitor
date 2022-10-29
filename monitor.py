import sys
import time
import data_class
from datetime import datetime, timedelta
from fritzconnection.lib.fritzhosts import FritzHosts

BAD_IPs = [
    '192.168.178.20', '192.168.178.21', '192.168.178.20', '192.168.178.22',
    '192.168.178.25', '192.168.178.24'
]
IP = '192.168.178.1'
PWD = 'xxxx'
try:
    MINUTES = int(sys.argv[1])
except:
    MINUTES = 30


def mon():
    device_list = get_device_info()
    last_print = get_dtn_min(-1)
    update_print = False
    update_event = []
    try:
        while True:
            dtn = get_dtn_min()
            # data stuff -> print_list
            act_device_list = get_device_info()
            for x in act_device_list:
                for d_l in device_list:
                    if x.ip == d_l.ip:
                        if d_l.active != x.active:
                            d_l.active = x.active
                            update_print = True
                            o = 'online' if x.active else 'offline'
                            s_e = data_class.status_event(
                                created=get_dtn_min(),
                                message=f'{x.name} is now {o}')
                            update_event.append(s_e)
                        if x.active:
                            d_l.last_online = dtn
            if dtn > last_print or update_print:
                print_list = []
                for x in device_list:
                    if x.last_online != None:
                        if get_dtn_min(-1 * MINUTES) < x.last_online:
                            print_list.append(x)
        # print
                if len(print_list) > 0:
                    print_devices(print_list)
                    print(
                        f'[{len(print_list)} devices connected within {MINUTES} minutes]'
                    )
                    for e in update_event:
                        print(f'[{e.created.strftime("%H:%M")}] [{e.message}]')
        # loop stuff
            update_print = False
            last_print = dtn
            # clear events
            update_event_temp = []
            for s_e in update_event:
                if get_dtn_min(-1 * MINUTES) < s_e.created:
                    update_event_temp.append(s_e)
            update_event = update_event_temp
            time.sleep(2.5)
    except KeyboardInterrupt:
        print('monitor closed by user.')


def get_device_info():
    fh = FritzHosts(address=IP, password=PWD)
    hosts = fh.get_hosts_info()
    devices = []
    for device in hosts:
        l_o = get_dtn_min() if device['status'] else None
        devices.append(
            data_class.device(id=None,
                              ip=device['ip'],
                              name=device['name'],
                              mac=device['mac'],
                              active=device['status'],
                              last_online=l_o))
    return devices


def get_dtn_min(min=0):
    d = datetime(datetime.now().year,
                 datetime.now().month,
                 datetime.now().day,
                 datetime.now().hour,
                 datetime.now().minute, 0, 0) + timedelta(minutes=min)
    return d


def print_devices(devices):
    dtn = get_dtn_min()
    print('\n' * 50)
    print(isalert(devices))
    print(f'[{dtn.strftime("%d.%m.%Y %H:%M")}]')
    print()
    devices.sort(key=get_ip)
    ip, name, mac = get_format_numbers(devices)
    print(
        f"{s_left('ip', ip)}{s_left('name', name)}{s_left('mac', mac)}status")
    count = 0
    for d in devices:
        count += 1
        if d.active:
            f_status = 'online'
        else:
            diff = dtn - d.last_online
            secs_diff = diff.total_seconds()
            min_diff = int(secs_diff / 60) % 60
            f_status = f'{min_diff} min offline'
        print(
            f'{s_left(d.ip, ip)}{s_left(d.name, name)}{s_left(d.mac, mac)}{f_status}'
        )
    print()


def get_ip(device):
    return int(str(device.ip).replace('.', ''))


def s_left(s: str, n: int):
    return s + ' ' * (n - len(s)) + '  '


def get_format_numbers(devices):
    ip, name, mac = 0, 0, 0
    for d in devices:
        ip = len(d.ip) if len(d.ip) > ip else ip
        name = len(d.name) if len(d.name) > name else name
        mac = len(d.mac) if len(d.mac) > mac else mac
    return ip, name, mac


def isalert(devices):
    for d in devices:
        for b_i in BAD_IPs:
            if d.ip == b_i and d.active:
                return '[danger]'
    return ''


if __name__ == '__main__':
    mon()
