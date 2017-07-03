#!/bin/bash
#Program: install_ansible.sh
#Author: Neal
#E_mail: 419775240@qq.com
#Date: 2016-07-06
#platform: Debian GNU/Linux 8 x64
#Version 1.0

#ansible installed?
ansible > /dev/null 2>&1
if [ $? -eq 0 ];then
    echo "ansible existing,please rerun after unloading"
    exit 1
fi

pwd=$PWD

#add user
if [[ ! `id ansible` ]];then
    useradd -m ansible -s /bin/bash
    echo "ansible:123456" | chpasswd
fi

#sudo set
ls /etc/sudoers > /dev/null 2>&1
if [ $? -ne 0 ];then
    apt-get -y install sudo
fi

grep "ansible ALL=(ALL:ALL) NOPASSWD: ALL"  /etc/sudoers > /dev/null 2>&1
[ $? -eq 0 ] && echo "ansible user is set sudo permissions." || sed -i "/^root/a\\ansible ALL=(ALL:ALL) NOPASSWD: ALL" /etc/sudoers


#Install dependencies
apt-get -y install build-essential autoconf libtool pkg-config python-opengl python-imaging python-pyrex python-pyside.qtopengl idle-python2.7 qt4-dev-tools qt4-designer libqtgui4 libqtcore4 libqt4-xml libqt4-test libqt4-script libqt4-network libqt4-dbus python-qt4 python-qt4-gl libgle3 python-dev libffi-dev  libssl-dev sshpass

#Compile the setuptools installation
echo "==========================================="
echo "install setuptools-26.0.0.tar.gz"
echo "==========================================="
ls /usr/local/setuptools-26.0.0 > /dev/null 2>&1
if [ $? -ne 0 ];then
    tar xf setuptools-26.0.0.tar.gz -C /usr/local
    [ $? -eq 0 ] && cd /usr/local/setuptools-26.0.0 && python setup.py install
fi


if [ $? -eq 0 ];then
    echo "setuptools-26.0.0 successful installation."
else
    echo "setuptools-26.0.0 install the abnormal!"
    exit 1
fi

#Compile the pyasnl installation
echo "==========================================="
echo "install pyasnl-0.1.9"
echo "==========================================="
tar xf pyasn1-0.1.9.tar.gz -C /usr/local
cd /usr/local/pyasn1-0.1.9 && python setup.py install

#Compile the ansible installation
echo "==========================================="
echo "install nsible-2.1.2.0"
echo "==========================================="
if [ $? -eq 0 ];then
    cd $pwd && tar xf ansible-2.1.2.0-0.1.rc1.tar.gz -C /usr/local && cd /usr/local/ansible-2.1.2.0 && python setup.py install
fi

#echo version
if [ $? -eq 0 ];then
    echo "ansible-2.1.2.0 successful installation."
    ansible --version
else
    echo "ansible-2.1.2.0 install the abnormal!"
    exit 1
fi
