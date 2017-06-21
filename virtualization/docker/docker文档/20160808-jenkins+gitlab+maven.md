##


zhaochj
passwd123!


参考文档：https://wiki.jenkins-ci.org/display/JENKINS/Use+Jenkins
war包下载地址：http://mirrors.jenkins-ci.org/war/


## jenkins安装

```
root@cst004 tools# pwd
/root/tools
root@cst004 tools# ls
jenkins_2.7.2_all.deb

#处理依赖
root@cst004 tools# aptitude install daemon however default-jre-headless openjdk-8-jre-headless
#安装
root@cst004 tools# dpkg -i jenkins_2.7.2_all.deb
```



## 访问

浏览器打开`http://172.31.10.24:8080`，如下图：

![Unlock](/images/jenkins-01.png)

```sh
root@cst004 tools# cat /var/lib/jenkins/secrets/initialAdminPassword
cab2ff67799c436487406650e622e6cb
```

把上边的密码输入解锁
