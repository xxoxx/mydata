[TOC]



# 处理依赖

```sh

root@auth-01:~# apt-get install libaio1

```



bin/mysqld --defaults-file=/data/mysqldata/3306/my.cnf --initialize-insecure --user=mysql --basedir=/usr/local/mysql --datadir=/data/mysqldata/3306/data --pid-file=/data/mysqldata/3306/pidfile/mysql.pid --socket=/data/mysqldata/3306/socketfile/mysql.sock


bin/mysqld --verbose --help   #查看帮助


bin/mysqld --defaults-file=/data/mysqldata/3306/my.cnf --initialize --user=mysql

bin/mysqld --defaults-file=/opt/mysql/mysql/etc/my.cnf  --initialize --user=mysql



错误：

mysql> show databases;

ERROR 1820 (HY000): You must reset your password using ALTER USER statement before executing this statement.

处理:

mysql> SET PASSWORD = PASSWORD('123456');



启动日志里有：

[Warning] TIMESTAMP with implicit DEFAULT value is deprecated. Please use --explicit_defaults_for_timestamp server option (see documentation for more details)

处理：

在配置文件中增加：

[mysqld]

explicit_defaults_for_timestamp=true
