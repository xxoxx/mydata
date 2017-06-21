[TOC]



## nginx反向代理registry



在基于TLS搭建docker registry.md中已实现基于TLS的方式实现一套docker registry。本文讲解如何实现在registry前端用nginx来反向代理，这更贴近实际的生产环境。



在registry主机上为了实现TLS，我们自建了CA，并为`registry.docker.kartor.cn`这个域名颁发了一个证书，证书和私钥存放在`/etc/docker/certs`，如下：



```sh
root@registry-01:/etc/docker/certs# ls
auth  registry.docker.kartor.cn.crt  registry.docker.kartor.cn.csr  registry.docker.kartor.cn.key
```



这里的证书和私钥在nginx主机会用到。



nginx在一台新主机上部署，版本不要太老，这里使用的版本如下：



```sh
root@nginx-01:/usr/local/nginx18/conf/layer7# nginx -v
nginx version: nginx/1.8.1
```



先把registry主相上的`registry.docker.kartor.cn`域名的证书和私钥copy到nginx主机上，存放目录自己规划，这里放在如下目录：



```sh
root@nginx-01:/usr/local/nginx18/conf/layer7/certs# pwd
/usr/local/nginx18/conf/layer7/certs
root@nginx-01:/usr/local/nginx18/conf/layer7/certs# ls
registry.docker.kartor.cn.crt  registry.docker.kartor.cn.key
```



nginx配置如下：



```sh

root@nginx-01:/usr/local/nginx18/conf/layer7# pwd

/usr/local/nginx18/conf/layer7
root@nginx-01:/usr/local/nginx18/conf/layer7# cat registry_docker_kartor_cn.conf
upstream registry {
    server 172.32.23.230:5000 weight=1;
    check interval=5000 rise=2 fall=5 timeout=1000 type=tcp port=5000;
}


server {
        listen       443 ssl;
        server_name  registry.docker.kartor.cn;

        access_log  logs/registry_docker_kartor_cn.access.log  main;
        error_log logs/registry_docker_kartor_cn.error.log debug;


        ssl_certificate      /usr/local/nginx18/conf/layer7/certs/registry.docker.kartor.cn.crt;
        ssl_certificate_key  /usr/local/nginx18/conf/layer7/certs/registry.docker.kartor.cn.key;

        ssl_session_cache    shared:SSL:1m;
        ssl_session_timeout  5m;

        ssl_ciphers  HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers  on;

        client_max_body_size 300m;

        chunked_transfer_encoding on;



        location / {
            proxy_pass https://registry/;
            proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
            proxy_redirect off;
            proxy_buffering off;
            proxy_set_header        Host            $http_host;
            proxy_set_header        X-Real-IP       $remote_addr;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        }

    }



root@nginx-01:/usr/local/nginx18/conf/layer7# nginx -t
nginx: the configuration file /usr/local/nginx18/conf/nginx.conf syntax is ok
nginx: configuration file /usr/local/nginx18/conf/nginx.conf test is successful
root@nginx-01:/usr/local/nginx18/conf/layer7# systemctl reload nginx.service
```



再在测试主机上测试，先修改`registry.docker.kartor.cn`域名的映射关系，即修改`/etc/hosts`，让该域名指向nginx主机的IP地址：



```sh

172.32.22.27    registry.docker.kartor.cn
#172.32.23.230    registry.docker.kartor.cn

```



push一个镜像测试，如下：



```sh
root@gdcp-01:/etc/docker# docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
tomcat              latest              a48852c0fc95        10 days ago         357.4 MB
root@gdcp-01:/etc/docker# docker tag tomcat:latest registry.docker.kartor.cn:443/application/tomcat:v1
root@gdcp-01:/etc/docker# docker push registry.docker.kartor.cn:443/application/tomcat:v1
The push refers to a repository [registry.docker.kartor.cn:443/application/tomcat]
Get https://registry.docker.kartor.cn:443/v1/_ping: x509: certificate signed by unknown authority
```



没有成功，报了‘certificate signed by unknown authority’，翻译过来是未授权的签署证书，在nginx的错误日志里也有以下日志输出：



```sh

2016/08/22 17:22:13 [info] 14216#0: *162 SSL_do_handshake() failed (SSL: error:14094412:SSL routines:SSL3_READ_BYTES:sslv3 alert bad certificate:SSL alert number 42) while SSL handshaking, client: 172.32.16.61, server: 0.0.0.0:443

```



这个问题排除了许久，首先想到是不是证书问题，但`registry.docker.kartor.cn.crt`和`registry.docker.kartor.cn.key`这两个文件是从registry主机上copy过来的，不应该有问题，并且也尝试重新copy，但问题依然。最后 查找资料发现是因为证书是我们自建CA为`registry.docker.kartor.cn`这个域名颁发，在docker看来，这种自建CA颁发的证书是不被信任的，是得不到docker承认的，所以我们需要把CA自己的证书导入到需要上传、下载docker镜像的主机的可信任证书列表中，centos系统是`/etc/ssl/certs/ca-bundle.crt`文件，debian系统是`/etc/ssl/certs/ca-certificates.crt`文件。





在registry主机（CA服务器）上获取CA的根证书：



```sh
root@registry-01:/etc/docker/certs# cat /etc/ssl/demoCA/cacert.pem
-----BEGIN CERTIFICATE-----
MIIDqTCCApGgAwIBAgIJAI8CDqK9xjfJMA0GCSqGSIb3DQEBCwUAMGsxCzAJBgNV
BAYTAkNOMRIwEAYDVQQIDAlDaG9uZ1FpbmcxDjAMBgNVBAcMBVl1QmVpMQ0wCwYD
VQQKDARTSktKMQswCQYDVQQLDAJDQTEcMBoGA1UEAwwTY2FzZXJ2aWNlLmthcnRv
ci5jbjAeFw0xNjA4MTkwMzQyNTVaFw0yNjA4MTcwMzQyNTVaMGsxCzAJBgNVBAYT
AkNOMRIwEAYDVQQIDAlDaG9uZ1FpbmcxDjAMBgNVBAcMBVl1QmVpMQ0wCwYDVQQK
DARTSktKMQswCQYDVQQLDAJDQTEcMBoGA1UEAwwTY2FzZXJ2aWNlLmthcnRvci5j
bjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAK7T1bRr6nVbt4allw1P
xBP7jKtHGKI0bP2YG0thzsCrFsHci/mL22FIp+uqAAFFoMhdoiSDOeBdIGnrRYPt
uosxh98ItWmnEo3FbJOKGIxHFvHZ3O1/TaopNqDAiCE7s2Y8D+p9iHRnVL0on69V
gSbn9PNCHYMklcOdn0laSnl+5dK8ZPbInXAaw383oXKqjelSEQtoW++zO6h6LW4j
mlQUTzFyr8INVGfmyF5VbP03g+K6mwh+5SWuLK3lHKscUGJ2Rkb0rm2HAR/pRLtl
wmogFWo9y0eGgAnsLQ6IdKZNlHJ+MPZAEREREyKZNDiS8O2QSHivpA90D+daBi9H
Zl0CAwEAAaNQME4wHQYDVR0OBBYEFESjdAJpS4K32DxZ8O09ANfZZ1F7MB8GA1Ud
IwQYMBaAFESjdAJpS4K32DxZ8O09ANfZZ1F7MAwGA1UdEwQFMAMBAf8wDQYJKoZI
hvcNAQELBQADggEBABkvrgF5fxkUavCBIOFvqNnOd/Kx9Mt1x3EHUns1hzrUxRFt
EvyuFqzUqbBTeG9jGvHY5RGlXN3UHbB2pKQp0hMcvMrNgfREgJ0h//mBeSHMMJ0A
MB+drdvbDKsNyxTdwvBRnYgEiXn/BJIhVedVV2wUVyDTFtQcCcMf+bjrRu/WgkhJ
nKAUTsS1zThm1RmhX2WG1mHooXzENjCeGcs2VvbbTACZGDPaqXhc0rrLLmQB69Bd
e6peWkFUpoaB2WSDWfakIYa4IBsvNV89D0zguO8sRIVFwYMLHPaw+KZYzFYK39w6
shpYI4R81Xdc/hg4sqp6kKaHNNNfn1kJweDuDek=
-----END CERTIFICATE-----
```



再把上边的内容追加到测试主机的`ca-certificates.crt`文件末尾，直接编辑此文件，把上边的内容复制到末尾，最后重启docker服务：



```
root@gdcp-01:/etc/docker# vim /etc/ssl/certs/ca-certificates.crt
# 把上边的cacert.pem文件内容追加到末尾

root@gdcp-01:/etc/docker# systemctl restart docker.service
```



再来测试一下看是否能push镜像：



```sh
root@gdcp-01:/etc/docker# docker push registry.docker.kartor.cn:443/application/tomcat:v1
The push refers to a repository [registry.docker.kartor.cn:443/application/tomcat]
e433cc54cfbc: Pushed
8a3e25fabd85: Pushed
1c900245f510: Pushed
9a329420f9ba: Pushed
615046ded065: Pushed
d6895f7becf9: Pushed
903bf3d7e2ff: Pushed
61f50980a4b2: Pushed
b5412699bc1b: Pushed
66d8e5ee400c: Pushed
2f71b45e4e25: Pushed
v1: digest: sha256:4b39c52437294a77e3035bd5fcfb71c54758065f58c5f9a088364c1e05ec549c size: 2624
```



push成功。





总结：



基于TLS搭建的docker registry，并使用了是自建CA来颁发证书，前端还使用了nginx作为反向代理，那在需要上传或下载的docker主机上所要做的配置如下：



1. CA的根证书要导入到`/etc/docker/certs.d/registry.docker.kartor.cn:5000/ca.crt`，其中`registry.docker.kartor.cn:5000`根据实际情况修改，这个即访问registry的域名；

2. CA根证书的内容要追加到可信任证书列表文件中，即`/etc/ssl/certs/ca-certificates.crt`这个文件。



最后重启docker服务即可正常访问registry



## 增加Basci Auth验证功能



创建用户密码存放路径，并创建用户及密码，如下：



```sh
root@nginx-01:/usr/local/nginx18# pwd
/usr/local/nginx18
root@nginx-01:/usr/local/nginx18# mkdir private
root@nginx-01:/usr/local/nginx18# htpasswd -cb /usr/local/nginx18/private/docker-auth.pass dockeruser dockerpasswd
```



如果没有htpasswd命令需要安装`apache2-utils`包。





在nginx配置文件中增加认证`auth_basic`和`auth_basic_user_file`两个参数，nginx的配置最后如下：



```sh
upstream registry {
    server 172.32.23.230:5000 weight=1;
    check interval=5000 rise=2 fall=5 timeout=1000 type=tcp port=5000;
}



server {
        listen       443 ssl;
        server_name  registry.docker.kartor.cn;

        access_log  logs/registry_docker_kartor_cn.access.log  main;
        error_log logs/registry_docker_kartor_cn.error.log debug;


        ssl_certificate      /usr/local/nginx18/conf/layer7/certs/registry.docker.kartor.cn.crt;
        ssl_certificate_key  /usr/local/nginx18/conf/layer7/certs/registry.docker.kartor.cn.key;

        ssl_session_cache    shared:SSL:1m;
        ssl_session_timeout  5m;

        ssl_ciphers  HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers  on;

        client_max_body_size 300m;

        chunked_transfer_encoding on;


        location / {
            auth_basic "Auth";
            auth_basic_user_file /usr/local/nginx18/private/docker-auth.pass;
            proxy_pass https://registry/;
            proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
            proxy_redirect off;
            proxy_buffering off;
            proxy_set_header        Host            $http_host;
            proxy_set_header        X-Real-IP       $remote_addr;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        }

    }



```

重启nginx，使配置生效：



```sh
root@nginx-01:/usr/local/nginx18# nginx -t
nginx: the configuration file /usr/local/nginx18/conf/nginx.conf syntax is ok
nginx: configuration file /usr/local/nginx18/conf/nginx.conf test is successful
root@nginx-01:/usr/local/nginx18# systemctl restart nginx.service
```



再在测试端上传一个镜像试一下，为了测试我先把之前上传的镜像在registry的存放上当删除并重启了`myregistry`容器，这样registry上没有任何镜像数据：



```sh
root@gdcp-01:~# docker push registry.docker.kartor.cn:443/application/tomcat:v1
The push refers to a repository [registry.docker.kartor.cn:443/application/tomcat]
e433cc54cfbc: Image push failed
e433cc54cfbc: Preparing
1c900245f510: Image push failed
9a329420f9ba: Image push failed
615046ded065: Image push failed
d6895f7becf9: Waiting
903bf3d7e2ff: Waiting
61f50980a4b2: Waiting
b5412699bc1b: Waiting
66d8e5ee400c: Waiting
2f71b45e4e25: Waiting
unauthorized: authentication required
```



认证失败，上传没有成功。需要先登陆再上传：



```sh
root@gdcp-01:~# docker login https://registry.docker.kartor.cn:443
Username (zhaochj): zhaochj
Password:
Login Succeeded
root@gdcp-01:~# docker push registry.docker.kartor.cn:443/application/tomcat:v1
The push refers to a repository [registry.docker.kartor.cn:443/application/tomcat]
e433cc54cfbc: Pushed
8a3e25fabd85: Pushed
1c900245f510: Pushed
9a329420f9ba: Pushed
615046ded065: Pushed
d6895f7becf9: Pushed
903bf3d7e2ff: Pushed
61f50980a4b2: Pushed
b5412699bc1b: Pushed
66d8e5ee400c: Pushed
2f71b45e4e25: Pushed
v1: digest: sha256:4b39c52437294a77e3035bd5fcfb71c54758065f58c5f9a088364c1e05ec549c size: 2624
```



登陆成功后上传成功。











[*参考*]



http://blog.coocla.org/docker-private-registry.html
http://ju.outofmemory.cn/entry/267508
http://blog.csdn.net/renhuailin/article/details/50461651
https://httpd.apache.org/docs/2.2/programs/htpasswd.html

