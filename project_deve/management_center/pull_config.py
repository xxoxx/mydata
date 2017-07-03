#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import os
import re
from kazoo.client import KazooClient


class Managedubbo(object):
    def __init__(self, zk_host):
        self.zk = KazooClient(hosts=zk_host, read_only=True)
        self.zk.start()

    def dubbo_group(self, path):
        duboo_group_lsit = self.zk.get_children(path)
        zk_origin_el = ['consumers', 'config', 'kafka', 'zookeeper']
        for el in zk_origin_el:
            duboo_group_lsit.remove(el)
        #print(duboo_group_lsit)
        test = ['keap']
        for i in duboo_group_lsit:
            #print(test)
            group_services = self.zk.get_children(os.path.join('/', i))
            for m in group_services:
                con_pro = self.zk.get_children(os.path.join('/', i, m))
                if 'providers' in con_pro:
                    path_providers = os.path.join('/', i, m, 'providers')
                if 'consumers' in con_pro:
                    path_consumers = os.path.join('/', i, m, 'consumers')
                provider_nodes = self.zk.get_children(path_providers)
                for x in provider_nodes:
                    provider_ip = re.search('([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])', x)
                    #print(''provider_ip.group(0))
                    print('{0} {1} {2}'.format(path_providers, provider_ip.group(0), len(provider_nodes)))


if __name__ == '__main__':
    manage = Managedubbo('172.31.11.21:2181')
    dubbo_groups = manage.dubbo_group('/')