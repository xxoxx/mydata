## LVS-HA ansible 部署

### 部署

　　首先ansible主控机需要与要部署集群环境的主机建立root用户的密钥认证，然后在anisble主控机上执行如下命令即可完成`lvs + keepalived`环境的搭建：
```sh
ansible@ansible:~/playbooks/initialize/deployment_environment$ pwd
/home/ansible/playbooks/initialize/deployment_environment
ansible@ansible:~/playbooks/initialize/deployment_environment$ ansible-playbook -i /home/ansible/playbooks/initialize/hosts_production site.yml -e "user=root app=lvs-ha"
```

其中`/home/ansible/playbooks/initialize/hosts_production`文件格式如下：
```
[mod_server]
172.31.10.113
172.31.10.114
```

各软件安装的版本如下：
- ipvsadm    1.26
- keepalived 1.2.13 

### 需要的高可用

　　在生产环境中，`lvs + keepalived`高可用服务架构希望应做到以下几点：

1. 先启动的节点成为MASTER节点，即使此节点的priority值比另一节点低，此节点的对外提供服务；
2. 后启动的节点成为BACKUP节点，即使此节点的priority值比另一节点高，此节点作为主节点的备节点；
3. BACKUP节点下线维护后重新上线，即使此节点的priority值比主节点高也不会抢占VIP资源；
4. 当主节点宕机、keepalived或lvs因意外不可用时，vip资源能迁移到备节点继续服务。


### role中keepalived.conf配置文件解析

　　在生产环境下LVS的高可一般有两个节点，这两个节点的`keepalived.conf`配置文件大部份相同，只有少数的配置参数不同。

　　模板中的`keepalived.conf`配置文件内容如下：

```sh
! Configuration File for keepalived

global_defs {
   router_id LVS_DEVEL
}

vrrp_sync_group VG1 {
  group {
    VI_1
  }
}

vrrp_instance VI_1 {
    state BACKUP
    interface eth0
    lvs_sync_daemon_interface eth0
    virtual_router_id 50
    nopreempt
    priority 150
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    virtual_ipaddress {
        10.0.0.1 dev eth0
    }
}

virtual_server 10.0.0.1 8888 {
    delay_loop 6
    lb_algo wlc
    lb_kind DR
    persistence_timeout 50
    protocol TCP

    real_server 10.0.100.2 8888 {
        weight 1
        TCP_CHECK {
            connect_timeout 10
        }
    }

    real_server 10.0.100.3 8888 {
        weight 1
        TCP_CHECK {
            connect_timeout 10
        }
   }
}
```

对以上的配置作如下解释：

1. `router_id LVS_DEVEL`表示主机标识，是一个全局配置，它只是一个名称，没有强制要求主备节点的这个名称不可以相同，一般我会取主机IP地址的最后一位来标识，比如主机的IP地址是`172.31.0.100`，那我会配置为`router_id LVS_100`；
2. `vrrp_sync_group VG1`确定失败切换（FailOver）包含的路由instance个数。即在有2个负载均衡器的场景，一旦某个负载均衡器失效，需要自动切换到另一个负载均衡器的实例是哪些？
3. `vrrp_instance VI_1`定义一个实例名称，此实例名称出自实例组中的group所包含的名称；
4. `state BACKUP`这是设置所在节点的vrrp`最初`的状态，有两种，MASTER和BACKUP，必须为大写，这只是在启动时标记节点的最初状态，当另一节点启动后会根据priority值进行选举，priority值大的才是真正的MASTER节点，所以state是MASTER还是BACKUP并不是特别重要;
5. `interface eth0`表示在内部网络中用来邦定用于传输vrrp的网络设置，如果主机有多个网卡可以与业务端口区分开；
6. `lvs_sync_daemon_interface eth0`表示负载均衡器之间的监控接口，类似于HA HeartBeat的心跳线。但它的机制优于 Heartbeat，因为它没有“裂脑”这个问题，它是以优先级这个机制来规避这个麻烦的。在DR模式中，lvs_sync_daemon_interface 与服务接口 interface 使用同一个网络接口；
7. `virtual_router_id 50` 这是虚拟路由的标识，是一个数字，范围为0..255,在同一个vrrp_instance中应使用唯一的标识，即在主备节点上的同一个vrrp实例中的virtual_router_id是相同的，并且一定要注意，在一个局域网中的不同的keepalived集群中也一定是唯一的；
8. `nopreempt`表示不抢占模式，此参数必须在节点为`state BACKUP`上配置，keepalived默认时一节点的下线维护后重新上线时，如果此节点的priority值比另一节点高，那启动后会抢占vip资源，也就是说优先级高的节点会最终成为MASTER节点；
9. `priority 150`表示优先级，数值越大，优先级越高，一般配置成`state MASTER`节点的priority值会比配置成`state BACKUP`节点的priority值高50，这只是官方的建议；
10. `advert_int 1`表示vrrp通知发送的间隔时间，单位为秒，默认为1秒；
11. `authentication {...}代码块`表示同一vrrp_instance的MASTER节点和BACKUP节点采用的验证类型，通常使用PASS，验证密码为明文，两个节点的密码必须相同才能相互通信；
12. `virtual_ipaddress {...}代码块`这里定义虚拟IP地址，即VIP，可以配置多个，一个IP占一行，可以指定此虚拟IP地址邦定在哪个接口上，这个IP地址和realserver上配置的虚拟IP地址要相同；
13. `virtual_server 10.0.0.1 8888 {...}代码块`声明一个虚拟服务，其中的ip地址是virtual_ipaddress定义的虚拟地址，端口是实际生产环境中业务所使用的端口号；
14. `delay_loop 6`延迟轮询时间，表示对real_server进行健康状态检测的间隔时间；
15. `lb_algo wlc`选择LVS的[调度算法](http://zhaochj.blog.51cto.com/368705/1643712)，这里选择wlc；
16. `lb_kind DR`定义LVS的转发模型，可选的有(NAT|DR|TUN)；
17. `persistence_timeout 50`定义持久连接的超时时间，单位为秒，此参数谨慎使用，启用此参数后客户端连接lvs，并被lvs采用指定的调度算法选择一个realserver进行响应，此客户端后端的请求都会在persistence_timeout时间内都不会受调度算法的影响而断续使用第一次响应的realserver进行响应，这样在大并发的场景下会在一定程度上打破负载均衡调度算法，比如我们这里采用wlc调度算法，各个real_server的weight都设置为1，理想状态下是后端的各real server的活动连接数几乎是一致的，但如果启用持久连接的超时这个参数，那负载均衡能力被打破，但这样在一定时间内实现了会话保持的功能，如何取舍，要根据实际的业务场景;
18. `protocol TCP`目前LVS只支持TCP转发；
19. `real_server 10.0.100.2 8888 {...}代码块`定义一个后端的real server，如果采用LVS的DR工作模型，那不支持端口映射，即这里的8888这个端口号必须与VIP对外提供服务的端口号一致；
20. `weight 1`设置此real server主机的权重，值越大，参与负载的机会就越大；
21. `TCP_CHECK {...}`设置healthcheckers的检测方式为tcp，即邦定IP地址和相应的端口来检测，默认对real_server里配置的ip和port进行检测，所以不需要指定`connect_ip <IP ADDRESS>`和`connect_port <PORT>`两个参数，对后端real server的检测方式有多种，有HTTP_GET|SSL_GET|TCP_CHECK|SMTP_CHECK|MISC_CHECK，这要根据实际的业务场景来选择；
22. `connect_timeout 10`配置对后端real server进行健康检测时的超时时间，不配置时，默认为5秒。

### 主备节点配置文件对比

　　在生产环境中应该尽量弱化keepalived的主备关系，即先启动哪个节点，那这个节点就是主节点对外提供服务，后启动的节点就是一个BACKUP角色，即使priority的值比第一个启动节点的值大也不要去抢占资源，要达到这样的需要，在两个节点中配置需要一点技巧。

`主机A`配置文件内容如下：

```host_A
! Configuration File for keepalived

global_defs {
   router_id LVS_HOST_A          <------
}

vrrp_sync_group VG1 {
  group {
    VI_1
  }
}

vrrp_instance VI_1 {
    state BACKUP
    interface eth0
    lvs_sync_daemon_interface eth0
    virtual_router_id 50
    priority 100                 <------
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    virtual_ipaddress {
        10.0.0.1 dev eth0
    }
}

virtual_server 10.0.0.1 8888 {
    delay_loop 6
    lb_algo wlc
    lb_kind DR
    persistence_timeout 50
    protocol TCP

    real_server 10.0.100.2 8888 {
        weight 1
        TCP_CHECK {
            connect_timeout 10
        }
    }

    real_server 10.0.100.3 8888 {
        weight 1
        TCP_CHECK {
            connect_timeout 10
        }
   }
}
```

`主机B`配置文件内容如下：

```host_B
! Configuration File for keepalived

global_defs {
   router_id LVS_HOST_B   <------
}

vrrp_sync_group VG1 {
  group {
    VI_1
  }
}

vrrp_instance VI_1 {
    state BACKUP
    interface eth0
    lvs_sync_daemon_interface eth0
    virtual_router_id 50
    nopreempt             <------
    priority 150          <------
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    virtual_ipaddress {
        10.0.0.1 dev eth0
    }
}

virtual_server 10.0.0.1 8888 {
    delay_loop 6
    lb_algo wlc
    lb_kind DR
    persistence_timeout 50
    protocol TCP

    real_server 10.0.100.2 8888 {
        weight 1
        TCP_CHECK {
            connect_timeout 10
        }
    }

    real_server 10.0.100.3 8888 {
        weight 1
        TCP_CHECK {
            connect_timeout 10
        }
   }
}
```

　　两主机配置不相同的地方已在配置文件中用`<------`标识出来，需要说明的是：

- `router_id `的值没有强制要求必须不同，只是为了区分两个节点而作的标识，在生产环境中可以提取主机名中的一部份来标识；

- `nopreempt`参数严格来说是配置在`state BACKUP`且`priority`值高于另一节点的节点上，但同时配置在了`priority`较小的节点上也不会产生错误，只是此参数不会起作用，因为此节点的`priority`值小，state又是`BACKUP`状态，所以根本就不会抢占资源;


### wlc算法缺点

　　wlc全名为Weighted Least-Connection Scheduling，表示带权重的最少连接调度算法，此调度算法会考虑到各个real server上的活动连接和非活动连接数，并尽可能按照各节点权重值的比例来调度，有一个公式可计算出各个real server上的负载，即：`Overhead=(Active*256+Inactive)/weighted`，从这个公式中可知道一个real server的开销值是活动连接数乘以256再加上非活动连接数的值再除以权重值。

　　试想这样一个场景，当一集群是新的业务系统，后端的各real server的系统配置不同，即对业务的处理能力不同，需要配置不同的weight值来区分，当一切配置妥当，启动keepalived服务时，因起初各real server的活动连接与非活动连接都是0，所以此时各real server的Overhead都是0，此时wlc算法就不会起作用，而是会根据`real_server IP PORT {...}`代码块配置的前后顺序来调度，如果把业务处理能力弱(即weight值小)的主机配置在前，那首先被调度到的就是这主机，而业务处理能力强的real server在起初没有被调度到，这个缺陷可以通过配置real_server的前后顺序来修复。

　　wlc算法在处理另一种场景时也不够了完美，一个处理大并发的lvs集群环境下，稳定工作一段时间后，有一天发现各real server都在高负荷运行，
此时需要向集群中增加real server节点，当把节点准备好，并修改keepalived.conf配置把此节点增加进来，此时reload了keepalived服务，这时瞬间
的新建连接都会落到新增加的节点上，极有可能超过了新节点的请求处理能力上限，而导致新节点系统崩溃，而更严重的是导致整个内部网络的颠覆，特
别是在`重虚拟化`的今天，LVS调度器极有可能是一个虚拟节点，共用了宿主机的网卡，如果此宿主机网络负荷本来就高，那有可能导致网络出现问题。
又因网络原因，一个real server与keepalived失联，keepalived已把此节点从自己的维护的节点列表中删除，但过了一会网络又恢复后，也依然会发生
瞬间请求集群在此节点上的现象。这是在大并发集群中可能会发生的事情，所以在这种大并发的集群环境下新增加节点要特别谨慎。~~有一些折衷的办法
能够处理这样的问题，在集群规划起初，各处理能力相同的real server的weight值不以1开始，应该配置一个较大的值，当有新节点(配置与之前的real 
server相同)增加时把些节点的weight值配置成一个较小的值，这样在一定程度上会降低瞬间并发落到新增加节点上，当各个real server按照weight值调
度得比较均衡时再修改这新节点的weight值与其他节点相同，再reload一下keepalived，这样让新增加节点的负载在时间上分开。~~

　　上边使用删除线的地方当时理解有误，因为wlc算法评估realsever负载的计算方式为`Overhead=(Active*256+Inactive)/weighted`，当新的realserver上线时不管weighted值如何，当时的活动连接和非活动连接都是零，那此主机的负载值为也为`0`，那reload后所有的新建连接也会被分发到新的realserver上，直到与之前的realserver达到平衡，但这就像上边所说的，在新增加的realserver不能够负载此时新增加的连接请求压力时就可能会导致`雪
崩效应`，最后把网络压垮，尤其在高并发的场景下，LVS使用了WLC算法，**一定不要动态的增加realserver。**
