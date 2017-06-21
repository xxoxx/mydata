http://www.cnblogs.com/565261641-fzh/p/5832041.html


## install software

### install goole chrome

[google-chrome-stable_current_amd64.deb](https://www.google.com/intl/en/chrome/browser/desktop/index.html)
```sh
sudo apt-get install libappindicator1 libindicator7
sudo apt-get install -f
sudo dpkg -i google-chrome-stable_current_amd64.deb
```


### install wine-qq
[wine-qqintl.zip](http://www.ubuntukylin.com/application/show.php?lang=cn&id=279)

```sh
sudo apt-get install -f
sudo dpkg -i fonts-wqy-microhei_0.2.0-beta-2_all.deb ttf-wqy-microhei_0.2.0-beta-2_all.deb wine-qqintl_0.1.3-2_i386.deb
```

### install qq for CrossOver

安装方法参考[这里](https://www.so-cools.com/?p=739)
安装包在`/home/neal/private/not-sync/software/实用工具`


1、处理依赖

```sh
sudo dpkg --add-architecture i386
sudo apt-get update
sudo apt-get install lib32z1 lib32ncurses5 libgif7:i386 libgl1-mesa-glx:i386 libssl1.0.0:i386 libgphoto2-6:i386
```

2、安装crossover

```sh
sudo dpkg -i crossover-15_15.0.3-1_all-free.deb

#若安装有错误，请尝试
apt-get install -f 自动尝试解依赖问题
```

3、安装deepin-crossover

```sh
tar xf deepin-crossover-helper.tar.gz
sudo dpkg -i deepin-crossover-helper_1.0deepin0_i386.deb

#若安装有错误，请尝试
apt-get install -f 自动尝试解依赖问题
```

4、安装QQ软件 apps.com.qq.im_8.1.17255deepin11_i386.deb   

```sh
sudo dpkg -i apps.com.qq.im_8.1.17255deepin11_i386.deb
#若安装有错误，请尝试
apt-get install -f 自动尝试解依赖问题
```

### wps 表格不能输入中文

电子表格不能输入中文：

```sh
neal@neal-System-Product-Name:~$ sudo vim /usr/bin/et
#!/bin/bash

export XMODIFIERS="@im=fcitx"     ---> 增加内容
export QT_IM_MODULE="fcitx"       ---> 增加内容
gOpt=
#gOptExt=-multiply
```
文字处理不能输入中文：

```sh
neal@neal-System-Product-Name:~$ sudo vim /usr/bin/wps
#!/bin/bash
export XMODIFIERS="@im=fcitx"    ---> 增加内容
export QT_IM_MODULE="fcitx"      ---> 增加内容

gOpt=
#gOptExt=-multiply
```

### 安装bcompare

[bcompare](http://www.scootersoftware.com/download.php)
[安装文档](http://www.scootersoftware.com/download.php?zz=kb_linux_install)

但是安装好后好像只有30天的试用期，网上有破解的key，但不是免费获取的。只好用wine来运行windows上的bcompare




### keepass2安装后中文乱码处理

1. keepass2建议采用apt-get install keepass2方式安装

2. 先把中文字体存放到:

```sh
neal@neal-System-Product-Name:~$ pwd
/home/neal
neal@neal-System-Product-Name:~$ ls .local/share/KeePass/
Chinese_Simplified.lngx
```

3. View -> Change Language -> Chinese_Simplified


4. Tools -> Options -> Interface -> 拉到最后把Force using system font (Unix only)的钩钩去掉即可


5. 重新启动


如果数据库文件是从windows系统上导入，且有中文，通过上边的修改后打以前的数据库，中文也不能正常显示，而是显示成一个个方框，处理如下：

Tools -> Optins -> Select List Font -> 选择一个中文字体(如：文泉驿米黑)


### UML工具安装

这样的工具在ubuntu下也不少，但我这里使用一个比较简单的工具,dia

```sh
neal@neal-System-Product-Name:~$ sudo apt-get install dia
```

**dia这个工具太难用**


### 画图工具 ，流程图，UML各种图形

[直接用chrome安装扩展即可](https://chrome.google.com/webstore/search/gliffy?hl=zh-CN)

### 远程连接工具pac manager，可替换SecureCRT/Putty等

[下载地址](https://sourceforge.net/projects/pacmanager/)
[官网](https://sites.google.com/site/davidtv/)
[安装参考文档](http://www.linuxidc.com/Linux/2014-04/100602.htm)

### 远程连接工具remmina

[安装](https://github.com/FreeRDP/Remmina/wiki)
