# 思考

zookeeper与kafka的集群搭建是一个简单但繁琐的工作，只要有过一次成功搭建的经验，只要仔细一点一般都能成功搭建一个zookeeper或kafka的集群环境。那这个过程能不能简化？让这个过程尽量自动化，让人少参与集群的配置操作。这里就用ansible的playbook来实现这一功能，只需运行一条命令，再品一口茶的功夫，一个可用的集群环境就被创建完成。

# 分析

这里来分析一下创建一个zookeeper集群和kakfa集群需要注意的点。

- zookeeper

zookeeper的集群配置有两点要注意：

1、 zoo.cfg配置文件中需要所有zookeeper的配置信息，格式为`server.1=zk_ip:2888:3888`，有几个zookeeper节点就有几行这样的配置，其中`zk_ip`表示zookeeper节点的ip地址，`server.`后边是一个数字，数字一般是递增的，这个数字与`zk_ip`形成一个对应；比如一个集群有5个节点，在zoo.cfg中需要有类似如下配置：

```sh
server.1=172.31.14.200:2888:3888
server.2=172.31.14.201:2888:3888
server.3=172.31.14.202:2888:3888
server.4=172.31.14.203:2888:3888
server.5=172.31.14.204:2888:3888
```
2、 在数据目录需要有一个名为`myid`的文件，数据目录是在zoo.cfg文件中`dataDir=`定义的目录路径，`myid`文件中的内容为该节点对应的`server.`后边的数字，比如`172.31.14.200`节点上就应该为数字1，`172.31.14.201`节点上就应该是数字2，依次这样。

- kafka

kafkka的集群配置有以下几点要注意：

1、 broker.id，是一个数字，不大于255，一般设置为节点IP地址的最后一位，比如`172.31.14.200`，那就设置成`broker.id=200`；

2、 `zookeeper.connect=`，这里填写zookeeper集群地址

所以要想实现zookeeper和kafka集群的自动部署则要实现配置文件的自动准备，使用ansible的template功能，再加上自定义的变量传递就可以实现。
所以整理出针对zookeeper集群所要传递的变量汇总后，hosts文件里应该是类似如下内容：

```sh
[servers]
172.31.14.200 node01=172.31.14.200 myid01=1 node02=172.31.14.201 myid02=2 node03=172.31.14.202 myid03=3 node04=172.31.14.203 myid04=4 node05=172.31.14.204 myid05=5
172.31.14.201 node01=172.31.14.200 myid01=1 node02=172.31.14.201 myid02=2 node03=172.31.14.202 myid03=3 node04=172.31.14.203 myid04=4 node05=172.31.14.204 myid05=5
172.31.14.202 node01=172.31.14.200 myid01=1 node02=172.31.14.201 myid02=2 node03=172.31.14.202 myid03=3 node04=172.31.14.203 myid04=4 node05=172.31.14.204 myid05=5
172.31.14.203 node01=172.31.14.200 myid01=1 node02=172.31.14.201 myid02=2 node03=172.31.14.202 myid03=3 node04=172.31.14.203 myid04=4 node05=172.31.14.204 myid05=5
172.31.14.204 node01=172.31.14.200 myid01=1 node02=172.31.14.201 myid02=2 node03=172.31.14.202 myid03=3 node04=172.31.14.203 myid04=4 node05=172.31.14.204 myid05=5
```
**注意**： 变量名称不能有横线`-`，短横线是ansible保留字符


针对kafka集群所要传递的变量汇总后，hosts文件里应该是类似如下内容：

```sh
[servers]
172.31.14.200  zk_connect=172.31.14.200:2181,172.31.14.201:2181,172.31.14.202:2181,172.31.14.203:2181,172.31.14.204:2181/kafka
172.31.14.201  zk_connect=172.31.14.200:2181,172.31.14.201:2181,172.31.14.202:2181,172.31.14.203:2181,172.31.14.204:2181/kafka
172.31.14.202  zk_connect=172.31.14.200:2181,172.31.14.201:2181,172.31.14.202:2181,172.31.14.203:2181,172.31.14.204:2181/kafka
172.31.14.203  zk_connect=172.31.14.200:2181,172.31.14.201:2181,172.31.14.202:2181,172.31.14.203:2181,172.31.14.204:2181/kafka
172.31.14.204  zk_connect=172.31.14.200:2181,172.31.14.201:2181,172.31.14.202:2181,172.31.14.203:2181,172.31.14.204:2181/kafka
```

# zookeeper-3.4.6角色实现

先来看一下zookeeper-3.4.6这个角色的目录结构，如下：

```sh
ansible@ansible:~/kartor/system_initialize/roles$ pwd
/home/ansible/kartor/system_initialize/roles
ansible@ansible:~/kartor/system_initialize/roles$ tree zookeeper-3.4.6/
zookeeper-3.4.6/
├── tasks
│   └── main.yml
└── templates
    ├── create_myid.sh.j2
    ├── zkServer.sh.j2
    ├── zk_start.sh.j2
    └── zoo.cfg.j2

2 directories, 5 files
```
就两个目录，5个文件而已，`tasks/main.yml`是任务清单，表示创建一个zookeeper集群所要做的一系列操作，`templates/zoo.cfg.j2`表示为每个节点准备`zoo.cfg`配置文件的模板文件，`templates/zkServer.sh.j2`是zookeeper启动脚本文件模板，不需要此模板也可以，这里只是修改了zookeeper启动时分配的内容大小，如果不做修改就保持默认值。`templstes/zk_start.sh.j2`这只是一个shell脚本，脚本实现把zookeeper节点部署好后启动zookeeper进程及配置在`/etc/rc.local`里实现开机自动启动。`templates/create_myid.sh.j2`这个shell脚本实现`myid`文件的创建。

把各个文件的内容展示在这里：

- main.yml

```
---

- block:
    - name: download zookeeper package from fileserver. tags --> down_zk
      get_url: url=http://{{ fileserver }}/zookeeper/zookeeper-3.4.6.tgz dest=/home/{{ user }}/bak/ group={{ user }} owner={{ user }}
      tags: down_zk

    - name: unarchive zookeeper-3.4.6.tgz. tags --> unarchive
      unarchive: src=/home/{{ user }}/bak/zookeeper-3.4.6.tgz dest=/home/{{ user }}/ copy=no group={{ user }} owner={{ user }}
      tags: unarchive

    - name: create a data directory. tags --> create_datalog
      file: dest=/home/{{ user }}/zk-data-logs state=directory group={{ user }} owner={{ user }}
      tags: create_datalog

    - name: prepare zoo.cfg file. tags --> prepare_cfg
      template: src=zoo.cfg.j2 dest=/home/{{ user }}/zookeeper-3.4.6/conf/zoo.cfg group={{ user }} owner={{ user }}
      tags: prepare_cfg

    - name: prepare the shell script to generate myid. tags --> prepare_build_myid_shell
      template: src=create_myid.sh.j2 dest=/tmp/create_myid.sh
      tags: prepare_build_myid_shell

    - name: execute create_myid.sh,build myid number. tags --> build_myid
      shell: /bin/bash /tmp/create_myid.sh
      tags: build_myid

    - name: prepare boot shell script. tags --> boot_script
      template: src=zkServer.sh.j2 dest=/home/{{ user }}/zookeeper-3.4.6/bin/zkServer.sh group={{ user }} owner={{ user }}
      tags: boot_script

    - name: prepare to start the shell script automatically. tags --> boot_script
      template: src=zk_start.sh.j2 dest=/home/{{ user }}/bin/zk_start.sh
      tags: boot_script

    - name: Check whether the configuration zookeeper start. tags --> check_zk_auto_start
      shell: grep "zk_start.sh" /etc/rc.local
      register: check_boot
      ignore_errors: True
      tags: check_zk_auto_start

    - name: configure power on vm boot zookeeper. tags --> poweron_boot
      shell: sed -i '/^exit 0/isudo -u {{ user }} /bin/bash /home/{{ user }}/bin/zk_start.sh' /etc/rc.local
      when: check_boot|failed
      tags: poweron_boot

    - name: boot zookeeper now. tags --> boot_zk
      shell: /bin/bash /home/{{ user }}/bin/zk_start.sh
      become: True
      become_user: "{{ user }}"
      tags: boot_zk

    - name: set scheduled tasks clean up log files. tags --> cron_clean_logs
      cron: name='clean data' minute={{ 59 |random(step=5) }} hour='{{ 6 |random }}' user={{ user }} job='/home/{{ user }}/zookeeper-3.4.6/bin/zkCleanup.sh /home/{{ user }}/zk-data-logs/version-2 2000'
      tags: cron_clean_logs


  when: ansible_distribution == "Debian" and ansible_distribution_major_version == "8"
  ```

- create_myid.sh.j2

```
#!/bin/bash
#Author: Neal
#Email: 419775240@qq.com
#Date: 2017-01-05
#Version 1.0

ip={{ ansible_eth0.ipv4.address }}
conf=/home/{{ user }}/zookeeper-3.4.6/conf/zoo.cfg
myid=`grep ${ip} ${conf}`
echo ${myid:7:1} > /home/{{ user }}/zk-data-logs/myid
```

- zkServer.sh.j2

这里文件只是在`#!/usr/bin/env bash`行的下一行加了以下内容：

```
{% if ansible_memtotal_mb >=2000 %}
export JVMFLAGS="-Xms512m -Xmx1024m $JVMFLAGS"
{% endif %}
```

- zk_start.sh.j2

```
#!/bin/bash
#Author: Neal
#Email: 419775240@qq.com
#Date: 2017-01-11

source /etc/profile

counter=$(jps | grep QuorumPeerMain | wc -l)
if [ "${counter}" = "0" ];then
    cd /home/{{ user }}/zookeeper-3.4.6/bin/
    ./zkServer.sh start
fi
```

- zoo.cfg.j2

这个文件中主要是定义zookeeper的数据目录的位置及zookeeper的集群定义，主要增加以下几行：

```
server.{{ myid01 }}={{ node01 }}:2888:3888
server.{{ myid02 }}={{ node02 }}:2888:3888
server.{{ myid03 }}={{ node03 }}:2888:3888
{% if myid04 is defined %}
server.{{ myid04 }}={{ node04 }}:2888:3888
{% endif %}
{% if myid05 is defined %}
server.{{ myid05 }}={{ node05 }}:2888:3888
{% endif %}
```
就是这里的配置实现了3节点或5节点的zookeeper集群的实现。

# kafka_2.10-0.9.0.1角色实现

kafka实现自动部署比zookeeper要简单，重点是实现broker.id的自动配置，目录结构如下：

```
ansible@ansible:~/kartor/system_initialize/roles$ tree kafka_2.10-0.9.0.1/
kafka_2.10-0.9.0.1/
├── tasks
│   └── main.yml
└── templates
    ├── generate_broker_id.sh.j2
    ├── kafka-server-start.sh.j2
    ├── kafka_start.sh.j2
    └── server.properties.j2

2 directories, 5 files
```
`main.yml`是任务列表，`generate_broker_id.sh.j2`模板是实现配置`broker.id`的shell脚本，因在同一套zookeeper管理的kafka集群中此id值是唯一的，我这里的策略是取节点eth0网络接口的ipv4地址的最后一位作为broker.id，`kafka-server-start.sh.j2`模板是kafka的启动脚本，这里面增加了java堆对内存的使用判断，`kafka_start.sh.m2`模板也是一个kafka的启动脚本，此脚本是当主机断电重启后被调用，`server.properties.j2`模板是kafka的属性配置文件。

内容展示：

- main.yml

```
---
- block:
    - name: download kafka package from fileserver. tags --> down_kafka
      get_url: url=http://{{ fileserver }}/kafka/kafka_2.10-0.9.0.1.tgz dest=/home/{{ user }}/bak/ group={{ user }} owner={{ user }}
      tags: down_kafka

    - name: unarchive kafka/kafka_2.10-0.9.0.1.tgz. tags --> unarchive
      unarchive: src=/home/{{ user }}/bak/kafka_2.10-0.9.0.1.tgz dest=/home/{{ user }}/ copy=no group={{ user }} owner={{ user }}
      tags: unarchive

    - name: create data directory. tags --> create_data_dir
      file: dest=/home/{{ user }}/kafka-09-logs state=directory group={{ user }} owner={{ user }}
      tags: create_data_dir

    - name: prepare server.properties file. tags --> prepare_server_properties
      template: src=server.properties.j2 dest=/home/{{ user }}/kafka_2.10-0.9.0.1/config/server.properties group={{ user }} owner={{ user }}
      tags: prepare_server_properties

    - name: copy prepare broker.id shell script. tags --> broker_id_shell
      template: src=generate_broker_id.sh.j2 dest=/tmp/generate_broker_id.sh group={{ user }} owner={{ user }}
      tags: broker_id_shell

    - name: execute generate_broker_id.sh. tags --> exec_shell
      shell: /bin/bash /tmp/generate_broker_id.sh
      tags: exec_shell

    - name: prepare kafka boot shell script. tags --> kafka_boot_shell
      template: src=kafka-server-start.sh.j2 dest=/home/{{ user }}/kafka_2.10-0.9.0.1/bin/kafka-server-start.sh
      tags: kafka_boot_shell

    - name: prepare to boot the shell script. tags --> poweron_boot_shell
      template: src=kafka_start.sh.j2 dest=/home/{{ user }}/bin/kafka_start.sh group={{ user }} owner={{ user }}
      tags: poweron_boot_shell

    - name: start kafka. tags --> start_kafka
      shell: /bin/bash /home/{{ user }}/bin/kafka_start.sh
      become: True
      become_user: "{{ user }}"
      tags: start_kafka

    - name: Check whether the configuration kafka start. tags --> check_zk_auto_start
      shell: grep "kafka_start.sh" /etc/rc.local
      register: check_boot
      ignore_errors: True
      tags: check_kafka_auto_start

    - name: configure power on boot kafka. tags --> poweron_boot
      shell: sed -i '/^exit 0/isudo -u {{ user }} /bin/bash /home/{{ user }}/bin/kafka_start.sh' /etc/rc.local
      when: check_boot|failed
      tags: poweron_boot

  when: ansible_distribution == "Debian" and ansible_distribution_major_version == "8"
  ```

- generate_broker_id.sh.j2


```
#!/bin/bash
#Author: Neal
#Email: 419775240@qq.com
#Date: 2017-01-05
#Version: 1.0

ip=`/sbin/ifconfig eth0 |sed -n '/inet addr/s/^[^:]*:\([0-9.]\{7,15\}\) .*/\1/p'`
broker_id=`echo ${ip##*.}`
if [ `grep "^broker.id=0" /home/{{ user }}/kafka_2.10-0.9.0.1/config/server.properties` ];then
    sed -i "s@broker.id=0@broker.id=${broker_id}@" /home/{{ user }}/kafka_2.10-0.9.0.1/config/server.properties
fi
```

- kafka-server-start.sh.j2

此启动脚本上对java所能使用的内容做的条件检测及配置，会比较灵活的根据系统内存大小来配置java所能使用的内存，条件判断语句如下：

```
if [ "x$KAFKA_HEAP_OPTS" = "x" ]; then
{% if ansible_memtotal_mb >=1024 and ansible_memtotal_mb < 2000 %}
    export KAFKA_HEAP_OPTS="-Xmx1G -Xms512M"
{% endif %}
{% if ansible_memtotal_mb >=3000 %}
    export KAFKA_HEAP_OPTS="-Xmx2G -Xms1G"
{% endif %}
fi
```

- kafka_start.sh.j2

```
#!/bin/bash
#Author: Neal
#Email: 419775240@qq.com
#Date: 2017-01-11

source /etc/profile

counter=$(jps | grep Kafka | wc -l)
if [ "${counter}" = "0" ];then
    cd /home/{{ user }}/kafka_2.10-0.9.0.1/
    bin/kafka-server-start.sh -daemon config/server.properties
fi
```

- server.properties.j2

此模板里主要实现zookeeper地址的自动配置，相关内容如下：

```
zookeeper.connect={{ zk_connect }}
```

# 如何使用

zookeeper与kafka这两个角色都编写好后，要想使用角色，还需要一个入口文件，入口文件需要与`roles`这个目录在同一级，其实它就是一个playbook，只是里面定义的不是一个个tasks，而是所要使用的roles名称，现在我们就来初始化一个zookeeper与kafka集群，如下：

```sh
ansible@ansible:~/kartor/system_initialize$ pwd
/home/ansible/kartor/system_initialize
ansible@ansible:~/kartor/system_initialize$ ls
README.md  roles  zcj_hosts_pre  zhaochj.yml
```
这里的`zhaochj.yml`就是入口文件，而`zcj_hosts_pre`就是最开始说的hosts文件，当然这些文件的名字可以随意取，`zcj_hosts_pre`的内容如下：

```sh
ansible@ansible:~/kartor/system_initialize$ cat zcj_hosts_pre
[servers]
172.31.14.200 node01=172.31.14.200 myid01=1 node02=172.31.14.201 myid02=2 node03=172.31.14.202 myid03=3 node04=172.31.14.203 myid04=4 node05=172.31.14.204 myid05=5
172.31.14.201 node01=172.31.14.200 myid01=1 node02=172.31.14.201 myid02=2 node03=172.31.14.202 myid03=3 node04=172.31.14.203 myid04=4 node05=172.31.14.204 myid05=5
172.31.14.202 node01=172.31.14.200 myid01=1 node02=172.31.14.201 myid02=2 node03=172.31.14.202 myid03=3 node04=172.31.14.203 myid04=4 node05=172.31.14.204 myid05=5
172.31.14.203 node01=172.31.14.200 myid01=1 node02=172.31.14.201 myid02=2 node03=172.31.14.202 myid03=3 node04=172.31.14.203 myid04=4 node05=172.31.14.204 myid05=5
172.31.14.204 node01=172.31.14.200 myid01=1 node02=172.31.14.201 myid02=2 node03=172.31.14.202 myid03=3 node04=172.31.14.203 myid04=4 node05=172.31.14.204 myid05=5

172.31.14.200  zk_connect=172.31.14.200:2181,172.31.14.201:2181,172.31.14.202:2181,172.31.14.203:2181,172.31.14.204:2181/kafka
172.31.14.201  zk_connect=172.31.14.200:2181,172.31.14.201:2181,172.31.14.202:2181,172.31.14.203:2181,172.31.14.204:2181/kafka
172.31.14.202  zk_connect=172.31.14.200:2181,172.31.14.201:2181,172.31.14.202:2181,172.31.14.203:2181,172.31.14.204:2181/kafka
172.31.14.203  zk_connect=172.31.14.200:2181,172.31.14.201:2181,172.31.14.202:2181,172.31.14.203:2181,172.31.14.204:2181/kafka
172.31.14.204  zk_connect=172.31.14.200:2181,172.31.14.201:2181,172.31.14.202:2181,172.31.14.203:2181,172.31.14.204:2181/kafka
```

这就是在`分析`阶段提及到的一些信息，roles中所需要的变量一部份就是从hosts文件中定义的，而还有一部分是从全局定义的，比如安装zookeeper及kafka的安装包在哪里来呢，在上边的`tasks/main.yml`中有这样一个字义：
```
- name: download kafka package from fileserver. tags --> down_kafka
  get_url: url=http://{{ fileserver }}/kafka/kafka_2.10-0.9.0.1.tgz dest=/home/{{ user }}/bak/ group={{ user }} owner={{ user }}
  tags: down_kafka
```
这里不是就定义了在哪里去下载相应的安装包，看起来像是一个http服务器提供了安装的下载，没错，就是一个http服务器，`{{ fileserver }}`就是一个全局变量，这样把一些安装包都集中的存放在http服务器上，与采用anisble自身的文件传输模块相比有一定的优势，当包比较大及操作的节点数比较多时，如果采用copy或synchronize这样的模块时发现ansible会大量占用cpu资源及带宽资源，如果把这些包放在一个http服务器上，能把这些压力转移出来，而对一个http服务器来说，决大部分占用的就是带宽资源而已。那这些全局变量是怎样来定义呢？来看一下入口文件的内容便知：

```sh
ansible@ansible:~/kartor/system_initialize$ cat zhaochj.yml
---
- hosts: servers
  remote_user: root
  vars:
    favcolor: blue
  vars_files:
    - roles/vars/global.yml
    - roles/vars/fileserver.yml

  roles:

    - common
    - jdk_public
    - jdk1.7.0_60
    - zookeeper-3.4.6

    #- common
    #- jdk_public
    #- jdk1.7.0_60
    - kafka_2.10-0.9.0.1
```

一看便知，代码块
```
vars:
  favcolor: blue
vars_files:
  - roles/vars/global.yml
  - roles/vars/fileserver.yml
```
就是定义局变量的，实际中可以把一些对所有或大部分角色都生效的变量抽取出来定义在一个文件中，然后像上边的代码块一样来导入。现在想初始化一个zookeeper和kafka环境只需执行如下命令：

```sh
nsible@ansible:~/kartor/system_initialize$ ansible-playbook -i zcj_hosts_pre zhaochj.yml -k -e "user=tomcat env=pre"
```

忘了说一点，因为实际的应用中你可以有好几个环境，而各个环境有些资源是不一样的，所以在`tasks/main.yml`文件中有些任务是加了`when: env=pre`这样的条件判断的，所以上边的执行命令需要传递这样一个参数来说明运行的环境。执行上边命令后等一会，一个zookeeper+kafka的集群环境就OK了。
