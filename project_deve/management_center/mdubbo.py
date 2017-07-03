#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import os
import re
import logging
from kazoo.client import KazooClient


class Managedubbo(object):
    def __init__(self, zk_host):
        try:
            self.zk = KazooClient(hosts=zk_host, read_only=True)
            self.zk.start(timeout=5)
        except Exception as e:
            logging.error(e)
        finally:
            logging.error('zookeeper is connection.')


def persistence(filename, string):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    with open(filename, 'a+') as f:
        f.write(string + '\n')


if __name__ == '__main__':
    level_2_no_children_file = '/tmp/dubbo/level_2_no_children.txt'
    level_3_no_children_file = '/tmp/dubbo/level_3_no_children.txt'
    level_4_no_children_file = '/tmp/dubbo/level_4_no_children.txt'
    no_consumers_ip_node = '/tmp/dubbo/no_consumers_ip_node.txt'
    consumers_not_in_node = '/tmp/dubbo/consumers_not_in_node.txt'
    providers_not_in_node = '/tmp/dubbo/providers_not_in_node.txt'
    no_providers_ip_node = '/tmp/dubbo/no_providers_ip_node.txt'
    providers_file = '/tmp/dubbo/providers_file.txt'
    consumers_file = '/tmp/dubbo/consumers_file.txt'

    M = Managedubbo(zk_host='172.31.11.21:2181')
    white_list = ['consumers', 'config', 'kafka', 'zookeeper']
    level_1 = M.zk.get_children('/')
    print(len(level_1))
    for w in white_list:
        level_1.remove(w)
    print(len(level_1))
    for i in level_1:
        path = os.path.join('/', i)
        level_2 = M.zk.get_children(path)
        if len(level_2) != 0:
            for m in level_2:
                path = os.path.join('/', i, m)
                level_3 = M.zk.get_children(path)
                if len(level_3) != 0:
                    if 'providers' in level_3:
                        path_p = os.path.join('/', i, m, 'providers')
                        reg_ip = '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])'
                        providers_lst = M.zk.get_children(path_p)
                        if len(providers_lst) != 0:
                            for n in providers_lst:
                                providers_ip = re.search(reg_ip, n)
                                persistence(providers_file, path_p + ' ' + providers_ip.group(0))
                        else:
                            persistence(no_providers_ip_node, path_p)
                    else:
                        persistence(providers_not_in_node, path)
                    if 'consumers' in level_3:
                        path_c = os.path.join('/', i, m, 'consumers')
                        consumers_lst = M.zk.get_children(path_c)
                        if len(consumers_lst) != 0:
                            for x in consumers_lst:
                                consumers_ip = re.search(reg_ip, x)
                                persistence(consumers_file, path_c + ' ' + consumers_ip.group(0))
                        else:
                            persistence(no_consumers_ip_node, path_c)
                    else:
                        persistence(consumers_not_in_node, path)
                else:
                    persistence(level_3_no_children_file, path)
        else:
            persistence(level_2_no_children_file, path)


