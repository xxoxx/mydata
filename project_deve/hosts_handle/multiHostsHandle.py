#!/home/neal/.pyenv/versions/env352/bin/python
# -*- coding: UTF-8 -*-

import re
import os
import logging
import threading


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s [%(threadName)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='multiHostsHandle.log',
                    filemode='a'
                    )


def resolver(hosts):
    """resolver函数解析hosts文件，返回已去重的IP地址列表"""
    s = set([])
    with open(hosts, 'r') as f:
        hosts_list = f.readlines()
        for i in hosts_list:
            sub_list = i.split()
            ip_rex = '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])' \
                     '\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])'
            if len(sub_list) > 0 and re.search(ip_rex, sub_list[0]):  # 排除空行和注释文字
                s.add(sub_list[0])
    return list(s)


def ping_check(ip):
    '''检测ip是否能ping通'''
    response = os.system('ping -c 1 ' + ip + '> /dev/null 2>&1')
    if response == 0:
        return True
    else:
        return False


if __name__ == '__main__':
    old_hosts = 'hosts'
    new_hosts = 'new_hosts'
    online_file = 'online_hosts.log'
    offline_file = 'offline_hosts.log'
    if os.path.exists(new_hosts):
        os.remove(new_hosts)
    if os.path.exists(online_file):
        os.remove(online_file)
    if os.path.exists(offline_file):
        os.remove(offline_file)

    ip_list = resolver(old_hosts)
    #print(ip_list)
    with open(offline_file, 'w+') as d:
        for ip in ip_list:
            t = threading.Thread(target=ping_check, name='worker-' + ip, args=(ip,))
            t.daemon = True
            t.start()
            t.join(timeout=1)


            #if not ping_check(ip):
            #   d.write(ip + '\n')

    with open(online_file, 'w+') as o:
        for ip in ip_list:
            if ping_check(ip):
                o.write(ip + '\n')

    with open(old_hosts, 'r') as old:
        old_hosts = old.readlines()

    with open(offline_file, 'r') as o:
        offline_hosts = o.readlines()

    with open(new_hosts, 'w+') as n:
        for i in old_hosts:
            e = i.split()
            if len(e) > 0 and e[0] + '\n' not in offline_hosts:
                n.write(i)
            if len(e) == 0:  # 空行直接写入文件
                n.write(i)



