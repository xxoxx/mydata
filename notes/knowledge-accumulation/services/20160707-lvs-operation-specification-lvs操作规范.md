## LVS操作规范

　　生产环境中部署LVS的架构为[LVS+KeepAlived](/documents/dep_environment/20160608-lvs+keepalived部署及配置文件解析.md)。LVS作为公司比
较核心的负载调度器，现对线上LVS的操作做如下要求。

- 绝对不允许动态增加realserver

　　在LVS已正常工作后，若想增加realserver的数量，那唯一的方法只能是找合适的时间停止keepalived服务，先停止备节点的服务，再停主节
点服务，再修改主备节点的`/etc/keepalived/keepalived.conf`配置文件，最后在启动keepalived前请仔细检查主备节点的keepalived.conf配置文件，若修改较大，建议使用`beyond compare`来对比主备节点的配置文件。若是删除节点理论上不会产生负面影响，但在操作前也要综合评估。

　　查看keepalived状态命令为：

```sh
root@lvs-master02:~# systemctl status keepalived.service
```

　　停止keepalived服务命令为：

```sh
root@lvs-master02:~# systemctl stop keepalived.service
```

　　启动keepalived服务命令为：

```sh 
root@lvs-master02:~# systemctl start keepalived.service
```

　　重新载入配置文件的命令为：

```sh 
root@lvs-master02:~# systemctl reload keepalived.service
```


　　修改了keepalived.conf配置文件后，因没有类似nginx的`nginx -t`的命令来检查配置文件语法的合法性，对keepalived.conf文件修改的正确全完全依赖维护者，若配置文件修改不正确会带来一些未知的问题，可能会加大故障排除的困难。对keepalived.conf配置文件的维护主要是增加或删除一个realserver，这里给出一个keepalived.conf的配置，如下：

```sh
global_defs {
    ... ...
}

vrrp_instance VI_1 {
    ... ....
}

virtual_server 172.31.0.130 8712 {
    ... ...

    real_server 172.31.0.188 8712 {
        weight 10
        TCP_CHECK {
            connect_timeout 10
        }
   }
    ... ...
}
```

特别注意各个代码块的范围，各个代码块以`{.. ...}`来区分，维护都需要维护的操作通常是`real_server IP PORT { ... }`这一块，当需要增加reals
erver节点时，就把`real_server IP PORT { ... }`复制后在其下边粘贴，再修改相应的`IP PORT`信息即可，当需要删除realserver节点时就把`real_server IP PORT { ... }`代码块删除。在使用`vim`这个编辑器编辑keepalived.conf文件时没有语法高亮显示，但建议维护人员要保持良好的代码缩进规
则，即`real_server IP PORT { ... }`区块相对于`virtual_server IP PORT`区块要空四个空格，`TCP_CHECK {...}`区块相对`real_server IP PORT { ... }`区块又要空四格，各realserver代码块间空一行来做间隔。


- 绝不保留已下线的realserver配置

　　当有realserver下线时请按照如下步骤操作：

1. 停止realserver节点的服务;

2. 在两LVS节点上删除此realserver的配置信息，keepalived服务不用重载，即不用执行`systemctl reload keepalived.service`命令；

3. 已下线realserver节点走下线资源回收流程。
