[TOC]





# 需求

公司内部各平台业务系统间可能会有接口调用(http请求)请求，各个业务系统模块往往不只是单个节点，采用nginx来对后端服务器节点做反向代理及负载均衡，因历史原因，未对每个业务平台搭建一套nginx对其他系统调用，而是多个业务平台混用一个nginx节点，此nginx节点存在单点问题，所以需要对此节点做改造，需要一套具有高可用的负载均衡系统。



# 实现思想



采用keepalived+nginx架构方式实现此套高可用方案，keepalived在三层提供一个虚拟IP地址对外提供服务，此IP邦定在哪个nginx节点上是通过keepalived的选举机制决定，keepalived通过灵活的健康检测机制决定触发相应的动作使用节点的权重发生改变，进而触发重新选举出新的master节点，使其虚拟ip进行飘移来保障业务的高可用性。



切换策略：

1. 提供正常服务的节点上一旦检测到nginx服务不可用时，首先尝试启动nginx服务；

2. 尝试启用nginx服务未成功时，直接停止keepalived进程(触发zabbix监控报警)，进而触发心跳检测到此节点的keepalived不可用后进行角色切换使用能正常工作的节点邦定虚拟IP地址，使服务的中断时间减少到最少

3. 对故障节点进行修复，启用nginx和keepalived服务后不强占虚拟IP地址，减少因强占虚拟IP带来的网络抖动



# 实战



主机节点信息：

| ip地址                              |   主机名                      |  备注              |
|---------------------------------|------------------------------|--------------------|
|172.31.14.82                    |nginx-01                        |  需安装keepalived |
|172.31.14.83                    |nginx-02                        |需安装keepalived
|172.31.13.242                  |                                      |    虚拟Ip地址          |



nginx与keepalived的安装省略。





- 提供检测nginx服务可用性的脚本



```sh
root@nginx-01:/etc/keepalived# pwd
/etc/keepalived
root@nginx-01:/etc/keepalived# ls
check_nginx.sh  keepalived.conf
root@nginx-01:/etc/keepalived# cat check_nginx.sh
#!/bin/bash
counter=$(ps -C nginx --no-heading|wc -l)
if [ "${counter}" = "0" ]; then
    /bin/systemctl start nginx.service
    sleep 1
    counter=$(ps -C nginx --no-heading|wc -l)
    if [ "${counter}" = "0" ]; then
        /bin/systemctl stop keepalived.service
    fi
fi
```

此脚本逻辑表示一旦检测到主机没有nginx进程存在时，先尝试启用nginx服务，如果1秒后再次检测nginx进程还是未存在，那就直接关闭keepalived服务。



- keepalived配置文件



```sh
root@nginx-01:/etc/keepalived# cat keepalived.conf
! Configuration File for keepalived
global_defs {
   router_id nginx-01
}
vrrp_script chk_nginx {
    script "/etc/keepalived/check_nginx.sh"
    interval 2
}
vrrp_instance VI_1 {
    state BACKUP
    interface eth0
    virtual_router_id 60
    nopreempt
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass qwert123!
    }
    virtual_ipaddress {
        172.31.13.242 dev eth0
    }
    track_script {
        chk_nginx
    }
}
```



配置参数说明：

1、`vrrp_script { }`代码块定义vrrp周期性调用的脚本，`interval`定义调用脚本的时间间隔，单位为秒

2、`state BACKUP`定义vrrp实例启动时的起始状态

3、`nopreempt`表示keepalived工作在非强占模式

4、`virtual_ipaddress { }`定义虚拟IP地址

5、`track_script { }`引用`vrrp_script{ }`定义的检测脚本

6、`advert_int` 表示心跳检测的时间间隔，单位为秒

7、`router_id` 表示路由(主机)的标志id，一般为主机的hotname



在`vrrp_instance VI_1 { }`没有使用`priority`来指定优先级，在测试时发现有无这个参数都没有影响，在日志中发现不配置此参数时默认是零。`nopreempt`这个参数显得比较重要，如果没有这个参数，那么当有一个keepalived工作时再启动另外的节点就会进行MASTER选举，此时`priority`参数才显得重要，这只是根据测试分析得到的结果。



**注意**

特别需要注意的是**检查nginx进程是否存在的脚本执行时间要小于`interval`定义的时间**，不然当下一个`interval`时间再来执行脚本进行检查时会发现上一个执行检查的脚本还没执行完，这会发生一些意想不到的结果，有可能nginx与keepalived进程都存在时发生了虚拟IP的切换。



在另一个nginx节点上`keepalived.conf`配置文件中的内容几乎一要，只需要把`router_id nginx-01`修改为`nginx-02`，这只是一个标识，用于启用`notification_email`参数时发送邮件所用，这个也没有强制要求修改。



# 测试



分别启动两个主机上的nginx和keepalived服务，启动没有先后顺序，先启动`keepalived`服务的主机上会邦定虚拟IP地址对外提供服务，现在是`nginx-02`主机上邦定了虚拟IP地址：

```sh

root@nginx-02:/etc/keepalived# ip add | grep eth0
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    inet 172.31.14.83/16 brd 172.31.255.255 scope global eth0
    inet 172.31.13.242/32 scope global eth0
```

测试nginx的主页：

```sh
ansible@ansible-01:~$ curl http://172.31.13.242:8134
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>
<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>
<p><em>Thank you for using nginx.</em></p>
</body>
</html>
```



直接关闭`nginx-02`上的nginx服务，再测试：

```sh
root@nginx-02:/etc/keepalived# cat /var/run/nginx18.pid
4969
root@nginx-02:/etc/keepalived# systemctl stop nginx.service && ps aux | grep nginx
root      5291  0.0  0.1  12728  2272 pts/0    R+   14:19   0:00 grep --color=auto nginx
root@nginx-02:/etc/keepalived# ps aux | grep nginx
root      5293  0.0  0.0   4336   808 ?        S    14:19   0:00 sh -c /etc/keepalived/check_nginx.sh
root      5294  0.0  0.1  21656  3336 ?        S    14:19   0:00 /bin/bash /etc/keepalived/check_nginx.sh
root      5303  0.0  0.0  31488   824 ?        Ss   14:19   0:00 nginx: master process /usr/local/nginx18/sbin/nginx -c /usr/local/nginx18/conf/nginx.conf
nginx     5304  1.0  0.9  48464 19532 ?        S    14:19   0:00 nginx: worker process
nginx     5305  0.0  0.9  48464 19532 ?        S    14:19   0:00 nginx: worker process
root      5308  0.0  0.1  12728  2304 pts/0    S+   14:19   0:00 grep --color=auto nginx
root@nginx-02:/etc/keepalived# cat /var/run/nginx18.pid
5303
```

关闭后再查看次查看，nginx的进程又被启动了，虚拟IP地址依然还是在`nginx-02`主机上：

```sh

root@nginx-02:/etc/keepalived# ip add | grep eth0
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    inet 172.31.14.83/16 brd 172.31.255.255 scope global eth0
    inet 172.31.13.242/32 scope global eth0
```

直接把`nginx-02`上的keepalived进程kill掉，观察虚拟IP地址是否会发生漂移：

```sh
root@nginx-02:/etc/keepalived# ps aux | grep keepalived
root     10133  0.0  0.0  51572  1428 ?        Ss   14:40   0:00 /usr/sbin/keepalived
root     10134  0.0  0.2  55740  5340 ?        S    14:40   0:00 /usr/sbin/keepalived
root     10135  0.2  0.1  55740  3992 ?        S    14:40   0:01 /usr/sbin/keepalived
root     12167  0.0  0.0  12728  2124 pts/0    R+   14:49   0:00 grep --color=auto keepalived
root@nginx-02:/etc/keepalived# killall keepalived
root@nginx-02:/etc/keepalived# ps aux | grep keepalived
root     12231  0.0  0.1  12728  2200 pts/0    S+   14:49   0:00 grep --color=auto keepalived
root@nginx-02:/etc/keepalived# ip add | grep eth0
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    inet 172.31.14.83/16 brd 172.31.255.255 scope global eth0
```

在`nginx-01`上查看是否有虚拟IP地址：

```sh

root@nginx-01:/etc/keepalived# ip add | grep eth0
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    inet 172.31.14.82/16 brd 172.31.255.255 scope global eth0
    inet 172.31.13.242/32 scope global eth0
```

虚拟IP地址被邦定了。



查看两边的日志：

```sh
# nginx-02
Dec 23 14:49:30 nginx-02 Keepalived_vrrp[10135]: VRRP_Instance(VI_1) sending 0 priority


# nginx-01
Dec 23 14:49:31 nginx-01 Keepalived_vrrp[26843]: VRRP_Instance(VI_1) Transition to MASTER STATE
Dec 23 14:49:32 nginx-01 Keepalived_vrrp[26843]: VRRP_Instance(VI_1) Entering MASTER STATE
```

nginx-01切换成了MASTER角色，nginx-02在被Kill后发送了一个为零的优先级。



测试nginx的主页依然能被访问。



# 方案优缺点



- 优点

1. keepalived的配置非常简单，易于维护

2. 初始状态两节点的角色都是BACKUP，且工作在非强占模式，当因故障发生虚拟IP发生切换后对有故障的节点进行维护后可放心启动keepalived服务，不会强制强占虚拟IP导致网络抖动



- 缺点

1. 角色为BACKUP的主机为热备份，不可接收外部的请求，资源浪费一半
