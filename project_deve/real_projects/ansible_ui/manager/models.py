from django.db import models

# Create your models here.


class Hosts(models.Model):
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    project_group = models.CharField(max_length=50, verbose_name='项目组')
    project_name = models.CharField(max_length=50, verbose_name='项目名称')
    environment = models.CharField(max_length=50, verbose_name='所属环境')
    port = models.IntegerField(default=8080, verbose_name='服务监听端口')
    service_status = models.BooleanField(default=0, verbose_name='服务状态')
    service_start_path = models.CharField(default='/home/tomcat/tomcat-7.0.54/bin/start.sh', max_length=80,
                                          verbose_name='服务启动脚本')
    service_stop_path = models.CharField(default='/home/tomcat/tomcat7.0.54/bin/stop.sh', max_length=80,
                                         verbose_name='服务停止脚本')
    svn_path = models.CharField(default='', max_length=100, verbose_name='代码svn存放路径')


def __str__(self):
    return self.ip_address

