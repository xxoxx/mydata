
- 当使用git clone来克隆一个项目时报`server certificate verification failed`：

```sh
tomcat@filter-01:/tmp/test$ git clone https://gitlab.kartor.cn/odm/environment-initialization.git

Cloning into 'environment-initialization'...

fatal: unable to access 'https://gitlab.kartor.cn/odm/environment-initialization.git/': server certificate verification failed. CAfile: /etc/ssl/certs/ca-certificates.crt CRLfile: none
```

处理：

```sh
export GIT_SSL_NO_VERIFY=1

#or

git config --global http.sslverify false

```
- 当要将一个已被git管理的文件加入`.gitignore`文件而使git不再管理此文件时，需要使用以下命令使git不再追踪此文件

```git
# git rm --cached 不被追踪的文件
```
