#!/bin/bash
#Program: ping_check.sh
#Author: Neal
#E_mail: sky_551@163.com
#Date: 2016-6-30
#Version 1.0

zk_list=(
iovpcv.kartor.zookeeper.node1
iovpcv.kartor.zookeeper.node2
iovpcv.kartor.zookeeper.node3
iovpcv.kartor.zookeeper.node4
iovpcv.kartor.zookeeper.node5
)


echo ".........ping check begin........" >> /tmp/ping_check.txt

while true;do
    for node in ${zk_list[@]};do
        ping -c 3 ${node} >> /dev/null 2>&1
        [ $? == 0 ] && echo "`date` - ${node} is up" >> /tmp/ping_check.txt || echo "`date` - ${node} is down" >> /tmp/ping_check.txt
    done
    sleep 2
done

