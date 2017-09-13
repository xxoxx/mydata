# 基于google-authenticator实现ssh的双因素验证

## 时间校准软件安装与配置

时间校准软件采用`chrony`,这是`ntp`协议的另一种实现,在openstack环境中也推荐使用.

```sh
[root@test-01 ~]# uname -a
Linux test-01 2.6.32-696.10.1.el6.x86_64 #1 SMP Tue Aug 22 18:51:35 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux
[root@test-01 ~]# yum install -y chrony
```
挑选一个较好的时服务器作为时间同步的源,时间服务器的选择可参考`http://www.pool.ntp.org/zone/asia`

```sh
[root@test-01 ~]# vim /etc/chrony.conf 
#server 0.rhel.pool.ntp.org iburst   #注释默认的,增加下边的时间服务器, 如果默认的可用也可不用修改
#server 1.rhel.pool.ntp.org iburst
#server 2.rhel.pool.ntp.org iburst
#server 3.rhel.pool.ntp.org iburst

server 0.cn.pool.ntp.org iburst
server 1.cn.pool.ntp.org iburst
server 2.cn.pool.ntp.org iburst
server 3.cn.pool.ntp.org iburst

# 其他保持默认

重启chrony服务及时间同步测试:

```

```sh
[root@test-01 ~]# /etc/init.d/chronyd restart

[root@test-01 ~]# chronyc sources
210 Number of sources = 4
MS Name/IP address         Stratum Poll Reach LastRx Last sample
===============================================================================
^- marla.ludost.net              2   6    77    36    +28ms[  +28ms] +/-  211ms
^* 85.199.214.100                1   6    77    37  -3727us[  -13ms] +/-  156ms
^+ ntp3.itcompliance.dk          3   6    77    35    +17ms[  +17ms] +/-  247ms
^+ 85.199.214.101                1   6    77    36  -1101us[-1101us] +/-  155ms

[root@test-01 ~]# date
星期三 九月 13 18:45:48 CST 2017
```

## 安装google的认证模块(google-authenticator-libpam)

- 处理依赖

```sh
[root@test-01 ~]# yum install -y git automake libtool pam-devel
```

- 编译安装

```sh
[root@test-01 ~]# git clone https://github.com/google/google-authenticator-libpam.git
[root@test-01 ~]# cd google-authenticator-libpam/
[root@test-01 google-authenticator-libpam]# ./bootstrap.sh
[root@test-01 google-authenticator-libpam]# make && make install
```

- pam及sshd认证配置

在`/etc/pam.d/sshd`文件的第一行加入`auth       required     pam_google_authenticator.so debug no_increment_hotp`, 如下:

```sh
[root@test-01 ~]#  vim /etc/pam.d/sshd
# google auth
auth       required     pam_google_authenticator.so debug no_increment_hotp
```

加入`debug`是便于排查问题.

创建软链接:

```sh
[root@test-01 ~]# ln -s /usr/local/lib/security/pam_google_authenticator.so /lib64/security/pam_google_authenticator.so
```

sshd开启认证选项:

```sh
[root@test-01 ~]#  vim /etc/ssh/sshd_config #确保开启以下几项

PasswordAuthentication yes
ChallengeResponseAuthentication yes
UsePAM yes
```

重启sshd服务使修改生效:

```sh
[root@test-01 ~]#  /etc/init.d/sshd restart
```

- 为当前用户初始化一次性认证 

```sh
[root@test-01 ~]# google-authenticator
Do you want authentication tokens to be time-based (y/n) y
Warning: pasting the following URL into your browser exposes the OTP secret to Google:
  https://www.google.com/chart?chs=200x200&chld=M|0&cht=qr&chl=otpauth://totp/root@neal.cn%3Fsecret%3DESPAS5ODM7PITGJJO2LAWABVGQ%26issuer%3Dneal.cn
Failed to use libqrencode to show QR code visually for scanning.
Consider typing the OTP secret into your app manually.
Your new secret key is: ESPAS5ODM7PITGJJO2LAWABVGQ
Your verification code is 640160
Your emergency scratch codes are:
  69435742
  91519052
  70751138
  97285249
  82873904

Do you want me to update your "/root/.google_authenticator" file? (y/n) y

Do you want to disallow multiple uses of the same authentication
token? This restricts you to one login about every 30s, but it increases
your chances to notice or even prevent man-in-the-middle attacks (y/n) y

By default, a new token is generated every 30 seconds by the mobile app.
In order to compensate for possible time-skew between the client and the server,
we allow an extra token before and after the current time. This allows for a
time skew of up to 30 seconds between authentication server and client. If you
experience problems with poor time synchronization, you can increase the window
from its default size of 3 permitted codes (one previous code, the current
code, the next code) to 17 permitted codes (the 8 previous codes, the current
code, and the 8 next codes). This will permit for a time skew of up to 4 minutes
between client and server.
Do you want to do so? (y/n) y

If the computer that you are logging into isn't hardened against brute-force
login attempts, you can enable rate-limiting for the authentication module.
By default, this limits attackers to no more than 3 login attempts every 30s.
Do you want to enable rate-limiting? (y/n) y
```

全部选择`y`, 并把以上的信息保存到安全的地方. 

`https://www.google.com/chart?chs=200x200&chld=M|0&cht=qr&chl=otpauth://totp/root@neal.cn%3Fsecret%3DESPAS5ODM7PITGJJO2LAWABVGQ%26issuer%3Dneal.cn`这是一个二维码图片,在手机的APP中可以扫码,如下:

![二维码](https://www.google.com/chart?chs=200x200&chld=M|0&cht=qr&chl=otpauth://totp/root@neal.cn%3Fsecret%3DESPAS5ODM7PITGJJO2LAWABVGQ%26issuer%3Dneal.cn)

```
Consider typing the OTP secret into your app manually.
Your new secret key is: ESPAS5ODM7PITGJJO2LAWABVGQ     #如果不使用二维码,可以使用这个key
Your verification code is 640160    # 这个不知到实际的用处
Your emergency scratch codes are:   # 下边的5个急救吗是当你手机掉后所用,使用一个就少一个
  69435742
  91519052
  70751138
  97285249
  82873904
```

## 手机安装验证器

android APP的下载地址: http://www.coolapk.com/apk/com.google.android.apps.authenticator2 

iphone手机在app strore中搜索`google authenticator`或`freeotp authenticator`进行安装.

APP安装好后就可以扫描生成的二维码或使用生成的Key来与google authenticator来协同工作, 一切准备好后退出登录,再次连接是为如下提示:

```sh
[root@test-01 ~]# ssh root@192.168.189.129
Verification code: 
```

让你输入`Verification code`, 这个就是你手机APP里的随机数字,有效期只有30秒.输入后回车,系统还会要求输入接入用户的密码,如下:

```sh
[root@test-01 ~]# ssh root@192.168.189.129
Verification code: 
Password:
```

这两个密码都正确的情况下才内登录系统.

## 可能遇到的错

在配置中如果遇到问题要仔细查看`/var/log/secure`这个日志.

- 错误一

```
[root@test-01 ~]# less /var/log/secure
Sep 13 13:49:21 neal sshd[2373]: error: PAM: Module is unknown for root from 192.168.189.140
Sep 13 13:49:28 neal unix_chkpwd[2378]: password check failed for user (root)
Sep 13 13:49:28 neal sshd[2377]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=192.168.189.140  user=root
Sep 13 13:49:30 neal sshd[2373]: error: PAM: Module is unknown for root from 192.168.189.140
Sep 13 13:49:37 neal unix_chkpwd[2380]: password check failed for user (root)
Sep 13 13:49:37 neal sshd[2379]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=192.168.189.140  user=root
Sep 13 13:49:39 neal sshd[2373]: error: PAM: Module is unknown for root from 192.168.189.140
Sep 13 13:49:47 neal sshd[2373]: Failed password for root from 192.168.189.140 port 52584 ssh2
Sep 13 13:49:55 neal sshd[2373]: Failed password for root from 192.168.189.140 port 52584 ssh2
Sep 13 13:49:56 neal sshd[2374]: Connection closed by 192.168.189.140
Sep 13 13:49:57 neal sshd[2383]: PAM unable to dlopen(/lib64/security/pam_google_authenticator.so): /lib64/security/pam_google_authenticator.so: cannot open shared object file: No such file or directory
Sep 13 13:49:57 neal sshd[2383]: PAM adding faulty module: /lib64/security/pam_google_authenticator.so
Sep 13 13:50:03 neal sshd[2383]: error: PAM: Module is unknown for root from 192.168.189.140
```

处理方法:

```sh
[root@test-01 ~]# find / -name pam_google_authenticator.so
/usr/local/lib/security/pam_google_authenticator.so
/root/google-authenticator-libpam/.libs/pam_google_authenticator.so

[root@test-01 ~]# ln -s /usr/local/lib/security/pam_google_authenticator.so /lib64/security/pam_google_authenticator.so
```

- 错误二

```sh
[root@test-01 ~]# less /var/log/secure
ep 13 14:32:06 neal sshd(pam_google_authenticator)[2772]: Did not receive verification code from user
Sep 13 14:32:06 neal sshd[2772]: error: ssh_msg_send: write
Sep 13 14:32:06 neal sshd(pam_google_authenticator)[2772]: Did not receive verification code from user
Sep 13 14:32:06 neal sshd(pam_google_authenticator)[2772]: Invalid verification code for root
Sep 13 14:32:06 neal sshd[2772]: error: ssh_msg_send: write
Sep 13 14:32:06 neal sshd[2772]: pam_unix(sshd:auth): conversation failed
Sep 13 14:32:06 neal sshd[2772]: pam_unix(sshd:auth): auth could not identify password for [root]
Sep 13 14:32:06 neal sshd[2772]: error: ssh_msg_send: write
```

如果收到以上的错误,那请检查服务器的时区是否与你的手机所在的时区是一致的,且服务器与手机的时间是否正确.


>> 参考文档

> http://shenyu.me/2016/09/05/centos-google-authenticator.html
> http://www.it165.net/os/html/201605/17022.html
> http://www.cnblogs.com/tiannan/p/6238832.html
> https://github.com/google/google-authenticator-libpam

