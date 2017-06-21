## 自建docker registry

   基于doceker官方的registry镜像搭建私有的仓库，便于企业内部镜像的集中管理。

测试环境如下：

```sh
root@cst006:~# cat /etc/issue
Debian GNU/Linux 8 \n \l

root@cst006:~# uname -a
Linux cst006 3.16.0-4-amd64 #1 SMP Debian 3.16.7-ckt20-1+deb8u1 (2015-12-14) x86_64 GNU/Linux
```

###  docker-engine安装

请参考[这里](https://zhaochj.github.io/docker-%E5%9F%BA%E7%A1%80/)

### docker registr部署

docker-engine版本如下：

```sh
root@cst006:~# docker version
Client:
 Version:      1.12.0
 API version:  1.24
 Go version:   go1.6.3
 Git commit:   8eab29e
 Built:        Thu Jul 28 21:40:59 2016
 OS/Arch:      linux/amd64

Server:
 Version:      1.12.0
 API version:  1.24
 Go version:   go1.6.3
 Git commit:   8eab29e
 Built:        Thu Jul 28 21:40:59 2016
 OS/Arch:      linux/amd64
 ```

* 安装docker加速器

因docker官方镜像源访问速度不稳定，所以采用[Daocloud](https://www.daocloud.io/)提供的[Docker加速器](https://www.daocloud.io/mirror#accelerator-doc)。执行如下命令即完成加速器的安装：

```sh
  root@cst006:~# curl -sSL https://get.daocloud.io/daotools/set_mirror.sh | sh -s http://b3c58bfd.m.daocloud.io
http://b3c58bfd.m.daocloud.io
Success.
You need to restart docker to take effect : sudo service docker restart
root@cst006:~# systemctl restart docker.service
```

目前好像也不可用了。

* 下载镜像及启动registry

```sh
root@cst006:~# docker search registry
NAME                                      DESCRIPTION                                     STARS     OFFICIAL   AUTOMATED
registry                                  Containerized docker registry                   1005      [OK]
konradkleine/docker-registry-frontend     Browse and modify your Docker registry in ...   104                  [OK]
atcol/docker-registry-ui                  A web UI for easy private/local Docker Reg...   82                   [OK]
distribution/registry                     WARNING: NOT the registry official image!!...   40                   [OK]

.........省略..................

root@cst006:~# docker pull registry
Using default tag: latest
latest: Pulling from library/registry
e110a4a17941: Pull complete
2ee5ed28ffa7: Pull complete
d1562c23a8aa: Pull complete
06ba8e23299f: Pull complete
802d2a9c64e8: Pull complete
Digest: sha256:1b68f0d54837c356e353efb04472bc0c9a60ae1c8178c9ce076b01d2930bcc5d
Status: Downloaded newer image for registry:latest

root@cst006:~# docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
registry            latest              c6c14b3960bd        2 weeks ago         33.31 MB
root@cst006:~# docker run -td --name myregistry -p 5000:5000 --restart=always registry:latest
45624a45263f520f918d44f437e0c047d70bedb11f0c782fcb647014ae23d940
root@cst006:~# docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
45624a45263f        registry:latest     "/entrypoint.sh /etc/"   5 seconds ago       Up 4 seconds        0.0.0.0:5000->5000/tcp   myregistry

root@cst006:~# curl http://127.0.0.1:5000   # 没有任何返回信息
root@cst006:~#

```

至此，regisry部署完成。关于`registry`这个镜像的详细信息请参考[这里](https://github.com/docker/distribution-library-image)

### docker registry测试

在别一个docker节点上事先在[时速云](https://hub.tenxcloud.com/repos/tenxcloud/tomcat)上下载了一个tomcat镜像，现在把这个镜像push到registry上，如下：

```sh
root@cst003:~# docker images
REPOSITORY                             TAG                 IMAGE ID            CREATED             SIZE
index.tenxcloud.com/tenxcloud/tomcat   latest              b381d2201788        3 months ago        544.6 MB

root@cst003:~# docker tag b381d2201788 172.31.10.36:5000/tenxcloud/tomcat
root@cst003:~# docker push 172.31.10.36:5000/tenxcloud/tomcat
The push refers to a repository [172.31.10.36:5000/tenxcloud/tomcat]
Get https://172.31.10.36:5000/v1/_ping: http: server gave HTTP response to HTTPS client
root@cst003:~#
```
上边的`docker push`没有成功，这里因为默认时，docker节点访问registry是需要基于https的安全访问，但在内部网络中完全可以只用http的访问，在[docker官网](https://docs.docker.com/registry/insecure/)有也相关说明，但按照官方的配置也没有成功，最后看到了[这篇](http://www.artificialworlds.net/blog/2015/08/27/changing-the-docker-daemon-options-in-systemd-on-ubuntu-15-04/)文章才解决了上边的问题。

解决方法如下：

```sh
root@cst003:~# vim /etc/systemd/system/multi-user.target.wants/docker.service
#把
ExecStart=/usr/bin/dockerd -H fd://
#修改成
ExecStart=
ExecStart=/usr/bin/dockerd -H fd:// --insecure-registry=172.31.10.36:5000
#172.31.10.36:5000 是registry的访问地址
```
再重启docker-engine:

```sh
root@cst003:~# systemctl daemon-reload
root@cst003:~# systemctl restart docker.service
```

再测试一下是否能push成功：

```sh
root@cst003:~# docker push 172.31.10.36:5000/tenxcloud/tomcat
The push refers to a repository [172.31.10.36:5000/tenxcloud/tomcat]
46fde93230c7: Pushed
0d8ff41a9462: Pushed
23ba025e38d5: Pushed
ee50095dc913: Pushed
944e7a5b76eb: Pushed
a9da4a436775: Pushed
1f3a66176e0c: Pushed
c9b3605120b3: Pushed
8b9b0944edba: Pushed
e3b0c44298fc: Pushed
5f70bf18a086: Pushed
5d26a4e3fd0f: Pushed
646a515ba220: Pushed
c678e945300c: Pushed
2c9b281afbbe: Pushed
874b676b3e0a: Pushed
latest: digest: sha256:c2307baeacc8ef33442b625131deb5b6c4b1837563d9f3c87dcec02dadc59810 size: 4274
```

推送成功。registry提供了简单的接口可以查看注册服务器中有哪些仓库，仓库中有哪些镜像，如下：

```sh
root@cst003:~# curl http://172.31.10.36:5000/v2/_catalog
{"repositories":["tenxcloud/tomcat"]}
root@cst003:~# curl http://172.31.10.36:5000/v2/tenxcloud/tomcat/tags/list
{"name":"tenxcloud/tomcat","tags":["latest"]}
```

再到另一个docker节点上测试一下能不能Pull刚才push镜像，如下：

```sh
root@cst004 ~# docker pull 172.31.10.36:5000/tenxcloud/tomcat
Using default tag: latest
latest: Pulling from tenxcloud/tomcat
a3ed95caeb02: Pull complete
8449ec4e4cd7: Pull complete
aa2f8df21433: Pull complete
e3cbbefa65f3: Pull complete
c9f371853f28: Pull complete
461710550b31: Pull complete
1775fca35fb6: Pull complete
e0a6feb9775e: Pull complete
fd9a5fdf69be: Pull complete
2e4c75503fb1: Pull complete
dffb7441d30b: Pull complete
8eb893116379: Pull complete
fdc684568e20: Pull complete
038ab74ae433: Pull complete
451cc5dd6688: Pull complete
61b41059930d: Pull complete
Digest: sha256:c2307baeacc8ef33442b625131deb5b6c4b1837563d9f3c87dcec02dadc59810
Status: Downloaded newer image for 172.31.10.36:5000/tenxcloud/tomcat:latest

root@cst004 ~# docker images
172.31.10.36:5000/tenxcloud/tomcat   latest              b381d2201788        3 months ago        544.6 MB
```

pull成功了，在pull前也要去修改`/etc/systemd/system/multi-user.target.wants/docker.service`，不然同样会报

> Error response from daemon: Get https://172.31.10.36:5000/v1/_ping: tls: oversized record received with length 20527

这样的错。
