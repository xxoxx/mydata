#/bin/bash
#Author: Neal
#Email: 419775240@qq.com
#Version: v1.0


cpu=`grep processor /proc/cpuinfo | wc -l`
mem=`cat /proc/meminfo | head -n 1 | awk '{print $2}'`
disk=`df -h | head -n 2 | tail -n 1 | awk '{print $2}'`
ip=`ip add show eth0 | grep "inet " | awk '{print $2}' | awk -F/ '{print $1}'`
name=`hostname`

echo -n $ip    $name    $cpu    $mem    $disk 
