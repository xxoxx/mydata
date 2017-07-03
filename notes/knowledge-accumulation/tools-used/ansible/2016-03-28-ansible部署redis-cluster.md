---
date: 2016-03-28 10:40
layout: post
title: deploy redis-cluster use ansible
categories: cluster
tags: redis-cluster
excerpt: deploy redis-cluster use ansible
---


# 简述

　　利用ansible工具完成redis-cluster环境部署主要包括两个部份，第一部份是针对linux主机一些内核参数的优化配置，第二部份是redis实例的部署。如果想了解更多关于redis的手动安装知识请参考[这里](http://zhaochj.blog.51cto.com/368705/1700892)。这次基于ansible工具完成redis-cluster环境的搭建所涉及到的系统、软件版本如下：

<pre><code>linux系统的： Debian 8.1 x64
reids版本： 3.0.5
</code></pre>

# 系统初始化

　　系统初始化时的通用设置不会在此文中体现，如果想了解系统的初化时做了哪些基础的配置请参考[这里](http://zhaochj.github.io/system-initialization-for-ansible/)，此文只是会说明要redis-cluster环境系统需要做哪些配置和优化。


redis-system 模块的目录结构如下：

<pre><code>ansible@ansible:/tmp/playbook$ pwd
/tmp/playbook
ansible@ansible:/tmp/playbook$ ll
total 8
drwxr-xr-x 3 ansible ansible 4096 Mar 28 15:18 deployment_environment
drwxr-xr-x 3 ansible ansible 4096 Mar 28 15:18 system-initialize

ansible@ansible:/tmp/playbook$ tree system-initialize/
system-initialize/
├── hosts
├── roles
│   └── redis_system
│       ├── files
│       │   ├── rc.local
│       │   ├── redis-3.2.2.gem
│       │   └── sysctl.conf
│       └── tasks
│           └── main.yml
└── site.yml

4 directories, 6 files
</code></pre>

rc.local文件增加了以下两语句，使开机关闭透明内存和执行时间同步命令：

<pre><code>echo never > /sys/kernel/mm/transparent_hugepage/enabled
/usr/sbin/ntpdate -u 192.168.0.254 > /tmp/cron_time.txt
</code></pre>

sysctl.conf文件增加了以下几个内核优化参数：

<pre><code>#最大队列长度，应付突发的大并发连接请求
net.core.somaxconn = 65535
#半连接队列长度，此值受限于内存大小
net.ipv4.tcp_max_syn_backlog = 20480
#内存分配策略
vm.overcommit_memory = 1
</code></pre>

main.yml文件内容如下：

<pre><code>
ansible@ansible:/tmp/playbook$ cat system-initialize/roles/redis_system/tasks/main.yml
---

#redis特有
- name: 配置sysctl.conf
  copy: src=sysctl.conf dest=/etc backup=yes
  when: ansible_distribution == "Debian" and ansible_distribution_major_version == "8"

- name: run sysctl -p
  shell: sysctl -p
  when: ansible_distribution == "Debian" and ansible_distribution_major_version == "8"

- name: close Transparent Huge Pages(THP)
  shell: echo never > /sys/kernel/mm/transparent_hugepage/enabled
  when: ansible_distribution == "Debian" and ansible_distribution_major_version == "8"

- name: exec shell after system runed
  copy: src=rc.local dest=/etc/ backup=yes

- name: install ruby
  apt: name=ruby-full force=yes state=present
  when: ansible_distribution == "Debian" and ansible_distribution_major_version == "8"
  tags: install_ruby-full

- name: under the ruby install redis interface for shell script
  copy: src=redis-3.2.2.gem dest=/tmp
  when: ansible_distribution == "Debian" and ansible_distribution_major_version == "8"
  tags: copy_redis322.gem

- name: add a user
  user: name={{ user }} password={{ passwd }} shell=/bin/bash
  tags: add_user

- name: rsync authorized keys
  authorized_key:
     key: "{{ lookup('file', '/home/ansible/.ssh/id_rsa.pub') }}"
     user: "{{ user }}"
     state: present
  tags: rsync_key

- name: change root password
  user: name=root password=$6$2Qdfjdkfjdaleeuriereruejrieru&&&R234(/dkfjdkf
  tags: chg_root_passwd_production
</code></pre>

site.yml文件内容如下：

<pre><code>---
- hosts: mod_server
  remote_user: root
  roles:
     - redis_system
</code></pre>

hosts文件里存放了哪些主机是需要初始化的主机列表，内容如下：

<pre><code>[mode_server]
192.168.10.22
192.168.10.23
192.168.10.24
192.168.10.25
192.168.10.26
192.168.10.27
</code></pre>

ansible的playbook已书写完整，那如何使用？只需要执行以下命令，并输入远程主机root用户密码就可对hosts文件中的主机列表完成系统初始化工作：
<pre><code>ansible@ansible:/tmp/playbook/system-initialize$ ansible-playbook site.yml -i hosts -u root -k
SSH password: 
</code></pre>

# redis实例部署和集群配置

dep_redis-3.0.5模块目录结构如下：

<pre><code>ansible@ansible:/tmp/playbook$ pwd
/tmp/playbook
ansible@ansible:/tmp/playbook$ ll
total 8
drwxr-xr-x 3 ansible ansible 4096 Mar 28 15:18 deployment_environment
drwxr-xr-x 3 ansible ansible 4096 Mar 28 15:18 system-initialize
ansible@ansible:/tmp/playbook$ tree deployment_environment/
deployment_environment/
├── hosts
├── roles
│   └── dep_redis-3.0.5
│       ├── files
│       │   └── redis-3.0.5
│       │       ├── bin
│       │       │   ├── config_redis_cluster.sh
│       │       │   ├── redis-benchmark
│       │       │   ├── redis-check-aof
│       │       │   ├── redis-check-dump
│       │       │   ├── redis-cli
│       │       │   ├── redis-sentinel
│       │       │   ├── redis-server
│       │       │   └── redis-trib.rb
│       │       └── redis.conf
│       ├── tasks
│       │   └── main.yml
│       └── templates
│           └── redis.conf.j2
└── site.yml

7 directories, 13 files
</code></pre>

main.yml内容如下：

<pre><code>ansible@ansible:/tmp/playbook$ cat deployment_environment/roles/dep_redis-3.0.5/tasks/main.yml
---
- name: 远程同步redis-3.0.5二进制包
  synchronize: src=redis-3.0.5/ dest={{ ansible_env.HOME }}/7000  checksum=yes compress=yes perms=yes
  tags: cpoy_packages

- name: 生成redis.conf文件
  template: src=redis.conf.j2 dest={{ ansible_env.HOME }}/7000/redis.conf
  tags: sync_redis.conf

- name: 启动redis实例
  shell: bin/redis-server redis.conf
  args:
      chdir: "{{ ansible_env.HOME }}/7000"
  tags: start_redis
</code></pre>

config_redis_cluster.sh脚本内容如下：

<pre><code>ansible@ansible:/tmp/playbook/roles$ cat deployment_environment/roles/dep_redis-3.0.5/files/redis-3.0.5/bin/config_redis_cluster.sh 
#!/bin/bash
#Program: config_redis_cluster.sh
#Author: Neal
#E_mail: 419775240@qq.com
#Date: 2016-2-23
#Version 1.0
#安装ruby下的redis接口，配置cluster-redis
# 本脚本用root用户运行

#本地redis.gem
ruby_redis=/tmp/redis-3.2.2.gem
#集群节点信息，请根据实际情况进行修改
node_0=192.168.x.x
port_0=7000
node_1=192.168.x.x
port_1=7000
node_2=192.168.x.x
port_2=7000
node_3=192.168.x.x
port_3=7000
node_4=192.168.x.x
port_4=7000
node_5=192.168.x.x
port_5=7000

#安装redis-3.2.2.gem
check_result=`/usr/bin/gem list --local | grep redis` > /dev/null 2>&1
if [[ ${check_result} == "redis (3.2.2)" ]];then
    echo "redis 接口已存在，不需要安装"
else    
    if [ -f ${ruby_redis} ];then
        /usr/bin/gem install --local ${ruby_redis} > /dev/null 2>&1
        [ $? -eq 0 ] && echo "ruby下的redis接口安装成功" || echo "ruby下的redis安装出现问题，请检查"
    else
        echo "${ruby_redis}文件不存在"
    fi
fi

#配置集群
/bin/su - redis -c "/home/redis/7000/bin/redis-trib.rb create --replicas 1 ${node_0}:${port_0} ${node_1}:${port_1} ${node_2}:${port_2} ${node_3}:${port_3} ${node_4}:${port_4} ${node_5}:${port_5}"
</code></pre>

**注意**

> config\_redis\_cluster.sh脚本完成ruby环境下redis接口的安装及redis cluster的创建，此脚本必须由root用户运行。

redis.conf.j2文件是一个模板文件，此文件中启用的配置参数如下：

<pre><code>ansible@ansible:/tmp/playbook$ egrep -v "#|^$" deployment_environment/roles/dep_redis-3.0.5/templates/redis.conf.j2
daemonize yes
pidfile /var/run/redis7000.pid
port 7000
tcp-backlog 511
bind {{ ansible_eth0.ipv4.address }}
timeout 0
tcp-keepalive 150
loglevel notice
logfile "redis.log"
databases 16
save ""
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./
slave-serve-stale-data yes
slave-read-only yes
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-disable-tcp-nodelay no
repl-backlog-size 512mb
slave-priority 100
maxclients 60000
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
lua-time-limit 5000
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 60000
cluster-require-full-coverage no
slowlog-log-slower-than 10000
slowlog-max-len 128
latency-monitor-threshold 0
notify-keyspace-events ""
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-entries 512
list-max-ziplist-value 64
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit slave 0 0 0
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
aof-rewrite-incremental-fsync yes
</code></pre>

site.yml文件内容如下：

<pre><code>- hosts: mod_server
  remote_user: '{{ user }}'

  roles:
     - dep_redis-3.0.5
</code></pre>

此处的hosts文件的格式与_系统初始化_时一样，

　　至此，redis实例的部署脚本准备妥当，那如何使用？命令如下：
<pre><code>ansible@ansible:/tmp/playbook/deployment_environment$ pwd
/tmp/playbook/deployment_environment
ansible@ansible:/tmp/playbook/deployment_environment$ ansible-playbook site.yml -i hosts -e "user=redis"
</code></pre>

　　到这里，各个节点上的redis的实例应该已启动起来了，并监听在7000端口，此时各节点的redis之间没有任何关系，现在需要修改 _config\_redis\_cluster.sh_ 脚本文件，把各个节点的IP地址修改成实际节点的IP地址，并切换到root用户运行此脚本完成redis cluster集群配置。


