## mysql的备份和还原


### innobackupex工具使用

- 安装

以centos 6为例 

```sh
wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm && rpm -ivh epel-release-latest-6.noarch.rpm
wget https://www.percona.com/downloads/XtraBackup/Percona-XtraBackup-2.4.4/binary/redhat/6/x86_64/percona-xtrabackup-24-2.4.4-1.el6.x86_64.rpm 
yum -y localinstall percona-xtrabackup-24-2.4.4-1.el6.x86_64.rpm --skip-broken
```


- 备份

```sh
/usr/bin/innobackupex --defaults-file=/opt/mysql/my.cnf --user=root --host=127.0.0.1  --port=3306 --socket=/opt/mysql/tmp/mysql.sock --password="XXXX"  /opt/bak

```

--defaults-file:  指向当前mysql的my.cnf文件所在路径, 这个选项必须放在第一个位置

这个命令是对数据库的全量进行备份，备份后会产生一个以当前时间命名的目录，如：2018-05-24_11-31-54




- 还原

在一个安装好对应版本的mysql后，先停止Mysqld进程，再把datadir目录下的数据移走。

把前边备份好的/opt/bak/2018-05-24_11-31-54目录copy到需要还原数据的主机上。

还原分成两步走，第一步，准备数据：


```sh
/usr/bin/innobackupex --defaults-file=/opt/mysql/my.cnf --use-memory=4G --apply-log /opt/bak/2018-05-24_11-31-54

```

数据大时可以加上`--use-memory=`参数，数据量小时可以不使用。


第二步，真正恢复数据：


```sh
/usr/bin/innobackupex --defaults-file=/opt/mysql/my.cnf --copy-back /opt/bak/2018-05-24_11-31-54
```

这样数据就会根据my.cnf配置的datadir目录把备份文件copy过去。

最后修改数据目录的权限, 比如：

```sh
chown -R mysql.mysql /opt/mysqldata/var
```


在真正还原数据这一步时，也可以直接把`/opt/bak/2018-05-24_11-31-54`目录下的所有数据copy到`/opt/mysqldata/var`下，并修改相应的权限。最后启动mysqld服务，观察错误日志是否有错。


