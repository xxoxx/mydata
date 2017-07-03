#!/bin/bash
#Program: down packages from svn
#Author: Neal
#E_mail: 419775240@qq.com
#Date: 2015-11-12
#Version 1.0
#现网环境svn地址：http://test.XXXX.cn:3690
#现网修改后的svn地址：http://XXXXX:XXXX

Svn_Path=$1
Temporary_Storage=/tmp/down_pkgs
Svn_Username=XXXX
Svn_Password=XXXX
Code_Storage_Directory=/ftproot/packages
Project_Name=`basename ${Svn_Path}`

#清理临时目录
rm -rf ${Temporary_Storage}/*
rm -rf ${Temporary_Storage}/.svn

#根据测试发送邮件的svn地址下载代码
/usr/bin/svn checkout --username ${Svn_Username} --password ${Svn_Password} ${Svn_Path} ${Temporary_Storage} > /dev/null
Return_1=`echo $?`

if [ ${Return_1} -eq 0 ];then
    if [ `ls ${Temporary_Storage} | wc -l` -eq 1 ];then
        Version=`ls ${Temporary_Storage}`
        echo -e "项目：\033[32m${Project_Name}\033[0m 版本：\033[32m${Version}\033[0m 已成功下载！"
    else
        echo -e "\033[33m程序版本号有问题，请检查${Temporary_Storage}下程序的版本号是否正确。\033[0m"
    fi
else
    echo -e "\033[33m代码下载有问题，请检查您的SVN下载地址！\033[0m"
    exit 1
fi

#获取项目版本号
Version=`ls ${Temporary_Storage}`

#################################当版本在/ftproot/packages已存在时用以下代码处理##########################################
#判断此版本在/ftproot/packages中是否存在，如果存在则退出
if [ -d ${Code_Storage_Directory}/${Project_Name}/${Version} ];then
    echo -e "您所将要升级的项目：\033[32m${Project_Name}\033[0m 版本：\033[32m${Version}\033[0m在${Code_Storage_Directory}中已存在。请检查！"
    echo -e  "是否需要重新覆盖代码，\033[32my\033[0m：是，\033[32mn\033[0m：否，请选择："
    read Choice
    if [ "${Choice}" == 'y' ];then
        #先删除已有的项目代码,再把代码mv到/ftproot/packages
        echo "删除版本"
        rm -rf ${Code_Storage_Directory}/${Project_Name}/${Version}
        sleep 10
        mv ${Temporary_Storage}/${Version} ${Code_Storage_Directory}/${Project_Name}
        echo -e "项目：\033[32m${Project_Name}\033[0m 版本：\033[32m${Version}\033[0m，代码已成功存放到${Code_Storage_Directory}目录!"
        exit 1
    elif [ "${Choice}" == 'n' ];then
        #清理已在运行svn客户端后产生的.svn和下载的代码
        rm -rf ${Temporary_Storage}/*
        rm -rf ${Temporary_Storage}/.svn
        exit 1
    else
        echo "您没有选择正确的操作！"
        exit 1
    fi
fi

#######################################当版本在/ftproot/packages下不存在时用以下代码处理###################################
#测试项目版本号是否为空,即测试svn客户端是否真正把代码下载到临时目录
if [ ${Version} ];then
    #测试项目及版本在/ftproot/packages目录下是否存在，如果不存在则创建
    [ -d ${Code_Storage_Directory}/${Project_Name} ] ||  mkdir -pv ${Code_Storage_Directory}/${Project_Name} > /dev/null
    mv ${Temporary_Storage}/${Version} ${Code_Storage_Directory}/${Project_Name}
    Return_2=`echo $?`

    #较验mv命令是否成功执行
    if [ ${Return_2} -eq 0 ];then
        echo -e "项目：\033[32m${Project_Name}\033[0m 版本：\033[32m${Version}\033[0m，代码已成功存放到${Code_Storage_Directory}目录!"
    else
        echo -e "\033[33m代码未能复制到${Code_Storage_Directory}目录!\033[0m"
        exit 1
    fi
else
    echo -e "\033[32m${Temporary_Storage}目录下没有相应版本的代码，请检查！\033[0m"
    exit 1
fi

#清理临时目录，因是用svn客户端下载代码，在/tmp/down_pkgs目录下有.svn目录
rm -rf ${Temporary_Storage}/.svn
