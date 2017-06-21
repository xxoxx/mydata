[TOC]



# influxdb



- 安装



```sh

root@influxdb-01:~# curl -sL https://repos.influxdata.com/influxdb.key | apt-key add - source /etc/os-release

root@influxdb-01:~# source /etc/os-release

root@influxdb-01:~# echo "deb https://repos.influxdata.com/debian jessie stable" |  tee /etc/apt/sources.list.d/influxdb.list

root@influxdb-01:~# apt-get update && apt-get install influxdb

E: The method driver /usr/lib/apt/methods/https could not be found.

N: Is the package apt-transport-https installed?

root@influxdb-01:~# apt-get install apt-transport-https

root@influxdb-01:~# apt-get update && apt-get install influxdb

```

```sh

root@influxdb-01:~# systemctl start influxdb.service 

root@influxdb-01:~# systemctl status influxdb.service 

● influxdb.service - InfluxDB is an open-source, distributed, time series database

   Loaded: loaded (/lib/systemd/system/influxdb.service; enabled)

   Active: active (running) since Sun 2016-12-25 11:17:48 CST; 2s ago

     Docs: https://docs.influxdata.com/influxdb/

 Main PID: 19417 (influxd)

   CGroup: /system.slice/influxdb.service

           └─19417 /usr/bin/influxd -config /etc/influxdb/influxdb.conf



Dec 25 11:17:48 influxdb-01 influxd[19417]: [shard-precreation] 2016/12/25 11:17:48 Starting precreation service with check interval of 10m0s, advance period of 30m0s

Dec 25 11:17:48 influxdb-01 influxd[19417]: [snapshot] 2016/12/25 11:17:48 Starting snapshot service

Dec 25 11:17:48 influxdb-01 influxd[19417]: [continuous_querier] 2016/12/25 11:17:48 Starting continuous query service

Dec 25 11:17:48 influxdb-01 influxd[19417]: [httpd] 2016/12/25 11:17:48 Starting HTTP service

Dec 25 11:17:48 influxdb-01 influxd[19417]: [httpd] 2016/12/25 11:17:48 Authentication enabled: false

Dec 25 11:17:48 influxdb-01 influxd[19417]: [httpd] 2016/12/25 11:17:48 Listening on HTTP: [::]:8086

Dec 25 11:17:48 influxdb-01 influxd[19417]: [retention] 2016/12/25 11:17:48 Starting retention policy enforcement service with check interval of 30m0s

Dec 25 11:17:48 influxdb-01 influxd[19417]: [monitor] 2016/12/25 11:17:48 Storing statistics in database '_internal' retention policy 'monitor', at interval 10s

Dec 25 11:17:48 influxdb-01 influxd[19417]: 2016/12/25 11:17:48 Sending usage statistics to usage.influxdata.com

Dec 25 11:17:48 influxdb-01 influxd[19417]: [run] 2016/12/25 11:17:48 Listening for signals

root@influxdb-01:~# ss -tnlp | grep influxd

LISTEN     0      128                      :::8086                    :::*      users:(("influxd",pid=19417,fd=5))

LISTEN     0      128                      :::8088                    :::*      users:(("influxd",pid=19417,fd=3))

```



- 创建数据库及用户

```sh

root@influxdb-01:~# influx -precision rfc3339

Visit https://enterprise.influxdata.com to register for updates, InfluxDB server management, and monitoring.

Connected to http://localhost:8086 version 1.1.1

InfluxDB shell version: 1.1.1

> create database k8s

> show databases

name: databases

name

----

_internal

k8s



> CREATE USER "root" WITH PASSWORD 'root' WITH ALL PRIVILEGES

> show users

user    admin

----    -----

root    true

```



# grafana



- 安装



```sh

root@influxdb-01:~/grafana# pwd

/root/grafana

root@influxdb-01:~/grafana# wget https://grafanarel.s3.amazonaws.com/builds/grafana_4.0.2-1481203731_amd64.deb

root@influxdb-01:~/grafana# apt-get install -y adduser libfontconfig

root@influxdb-01:~/grafana# dpkg -i grafana_4.0.2-1481203731_amd64.deb

root@influxdb-01:~/grafana# dpkg -i grafana_4.0.2-1481203731_amd64.deb

Selecting previously unselected package grafana.

(Reading database ... 32799 files and directories currently installed.)

Preparing to unpack grafana_4.0.2-1481203731_amd64.deb ...

Unpacking grafana (4.0.2-1481203731) ...

Setting up grafana (4.0.2-1481203731) ...

Adding system user `grafana' (UID 109) ...

Adding new user `grafana' (UID 109) with group `grafana' ...

Not creating home directory `/usr/share/grafana'.

### NOT starting on installation, please execute the following statements to configure grafana to start automatically using systemd

 sudo /bin/systemctl daemon-reload

 sudo /bin/systemctl enable grafana-server

### You can start grafana-server by executing

 sudo /bin/systemctl start grafana-server

Processing triggers for systemd (215-17+deb8u1) ...

```

```sh

root@influxdb-01:~/grafana# systemctl daemon-reload 

root@influxdb-01:~/grafana# systemctl enable grafana-server

Synchronizing state for grafana-server.service with sysvinit using update-rc.d...

Executing /usr/sbin/update-rc.d grafana-server defaults

Executing /usr/sbin/update-rc.d grafana-server enable

Created symlink from /etc/systemd/system/multi-user.target.wants/grafana-server.service to /usr/lib/systemd/system/grafana-server.service.

root@influxdb-01:~/grafana# systemctl start grafana-server.service 


root@influxdb-01:~/grafana# ss -tnlp | grep grafana

LISTEN     0      128                      :::3000                    :::*      users:(("grafana-server",pid=20101,fd=9))

```


