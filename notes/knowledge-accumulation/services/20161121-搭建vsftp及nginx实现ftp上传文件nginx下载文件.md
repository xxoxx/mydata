[TOC]





# 需求描述



车机与行车记录仪连接后取得照片，车机把照片传回到ftp服务器，开放平台能过http的文件获取到图片。



主机：172.16.1.35



# vsftp配置部分



## vsftp服务安装及配置



```sh

root@tomcat-01:~# apt-get install vsftpd

root@tomcat-01:~# vsftpd -v

vsftpd: version 3.0.2


root@tomcat-01:~# cat /etc/vsftpd.conf

anonymous_enable=NO



local_enable=YES

write_enable=YES

local_umask=022



xferlog_enable=YES

xferlog_file=/var/log/vsftpd.log

xferlog_std_format=YES



idle_session_timeout=600

data_connection_timeout=300

accept_timeout=60

max_clients=10

max_per_ip=3



pasv_enable=YES

pasv_min_port=3000

pasv_max_port=3050



ftpd_banner=Welcome to FTP service.



chroot_local_user=YES

local_root=/ftproot/mydata/images

chroot_list_enable=YES

chroot_list_file=/etc/vsftpd.chroot_list

allow_writeable_chroot=YES



listen=YES

listen_port=2121



pam_service_name=vsftpd

userlist_enable=YES

userlist_file=/etc/ftpusers

```

配置文件上配置了`chroot_local_user=YES`和`chroot_list_enable=YES`，表示默认所有ftp用户都被限制在`local_root`目录下，如果要取消这种限制则需要把用户名写入到`chroot_list_file`指定的文件中。在新版本的vsftp中如果启用了chroot功能就需要要开启`allow_writeable_chroot=YES`这个选项。



创建/etc/vsftpd.chroot_list文件：



```sh

root@tomcat-01:~# touch /etc/vsftpd.chroot_list

```



## ftp主目录规划及权限设定



```sh

root@tomcat-01:~# mkdir -pv /ftproot/mydata/images

root@tomcat-01:~# setfacl -R -m g:ftp:rwx /ftproot/mydata/images

```

ftp主目录规划属于ftp组的用户都具有rwx的权限。



## 创建ftp登陆用户



```

root@tomcat-01:~#  useradd -m -g ftp ftpuser01

root@tomcat-01:~#  passwd ftpuser01

```

本想在创建用户时指定shell为`/usr/sbin/nologin`但经测试这样创建的用户不能正常登陆ftp，报`530 Login incorrect.`错误。



# nginx配置部分



nginx在这里充当静态页面下载服务器，只需要新创建一个server，加上几个相应的参数配置即可：

```

server {

    listen   9210; 

    server_name localhost;

    root /ftproot/mydata/images;

    autoindex on;

    autoindex_exact_size off;

    autoindex_localtime on;

}

```
