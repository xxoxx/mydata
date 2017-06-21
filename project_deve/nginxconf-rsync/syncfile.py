import time
import os
import logging
import paramiko
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='rsync_nginx.log',
                    filemode='a'
                    )


class Sftper(object):
    def __init__(self, hostname, port, username, key_file):
        self.key = paramiko.RSAKey.from_private_key_file(key_file)
        self.t = paramiko.Transport((hostname, port))
        self.t.connect(username=username, pkey=self.key)
        self.sftp = paramiko.SFTPClient.from_transport(self.t)

    def put(self, src_path, dest_path):
        self.sftp.put(src_path, dest_path)

    def close(self):
        self.sftp.close()


class Execer(object):
    def __init__(self, hostname, port, username, key_file):
        self.key = paramiko.RSAKey.from_private_key_file(key_file)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.load_system_host_keys()
        self.ssh.connect(hostname, port, username, pkey=self.key, timeout=10)

    def exec(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        cmd_result = stdout.read(), stderr.read()   # cmd_result is a tuple
        for line in cmd_result:
            logging.info('Command execution output - {0}'.format(line.decode()))

    def nginx_syntax_check(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        cmd_result = stdout.read(), stderr.read()   # cmd_result is a tuple
        for line in cmd_result:
            #print(line.decode())
            if 'test is successful' in line.decode():
                logging.info('check nginx confige is ok, will being reload remote host nginx config')
                self.ssh.exec_command('/usr/local/nginx18/sbin/nginx -s reload')


class Rsyncer(FileSystemEventHandler):
    def __init__(self, sftper, execer):
        self.sftper = sftper
        self.execer = execer

    def on_moved(self, event):
        #print(event.src_path, event.dest_path)
        if not os.path.basename(event.dest_path).endswith('~') and not os.path.basename(event.src_path).startswith('sed'):
            self.execer.exec('mv' + ' ' + event.src_path + ' ' + event.dest_path)
            self.execer.nginx_syntax_check('/usr/local/nginx18/sbin/nginx -t')
        if os.path.basename(event.src_path).startswith('sed'):
            """当用sed命令来修改文件时，sed会把原文件copy成一个以sed开头的文件，修改结束后会把这个文件重命令为原文件名"""
            logging.info('user sed commmand modify confige, {0} will be scp to remote host'.format(event.dest_path))
            self.sftper.put(event.dest_path, event.dest_path)
            self.execer.nginx_syntax_check('/usr/local/nginx18/sbin/nginx -t')

    def on_created(self, event):
        """http://pythonhosted.org/watchdog/api.html#module-watchdog.events"""
        if os.path.isdir(event.src_path):
            logging.info('create director - {0}, will be {1} touch the directory'.format(event.src_path, hostname))
            self.execer.exec('mkdir' + ' ' + '-pv' + ' ' + event.src_path)
        if os.path.isfile(event.src_path):
            if not os.path.basename(event.src_path).startswith('.') \
                    and not os.path.basename(event.src_path).endswith('~')\
                    and not os.path.basename(event.src_path).startswith('sed'):
                """当使用sed命令修改配置文件中的内容时系统会先创建一个以“sed”开头的文件，当修改完成后会把这个"sed"开头的文件名修改成原文件名"""
                logging.info('create file - {0}, will be scp to {1}'.format(event.src_path, hostname))
                self.sftper.put(event.src_path, event.src_path)
                self.execer.nginx_syntax_check('/usr/local/nginx18/sbin/nginx -t')

    def on_deleted(self, event):
        if not os.path.basename(event.src_path).endswith('~') \
                and not os.path.basename(event.src_path).endswith('.swp') \
                and not os.path.basename(event.src_path).endswith('.swx') \
                and not os.path.basename(event.src_path).endswith('.swpx') \
                and not os.path.basename(event.src_path).isdigit():
            logging.info('delete file {0}, will move {0} to /tmp/nginx_conf_bak'.format(event.src_path))
            self.execer.exec('mv' + ' ' + event.src_path + ' ' + '/tmp/nginx_conf_bak')
            self.execer.nginx_syntax_check('/usr/local/nginx18/sbin/nginx -t')

    def on_modified(self, event):
        #print('modified is {0}'.format(event.src_path))
        if os.path.isdir(event.src_path):
            logging.info('modify the directory, will be ignored. - {0}'.format(event.src_path))
        if os.path.isfile(event.src_path) and not os.path.basename(event.src_path).endswith('.swp'):
            logging.info('modify the file - {0}, will be scp to {1}'.format(event.src_path, hostname))
            # 修改一个文件,watchdog也监控是创建一个文件,此处可不做处理


if __name__ == '__main__':
    hostname = '172.31.0.9'
    port = 22
    username = 'root'
    key_file = '/home/neal/.ssh/id_rsa'
    path = '/usr/local/nginx18/conf'
    observer = Observer()
    sftper = Sftper(hostname, port, username, key_file)
    execer = Execer(hostname, port, username, key_file)
    try:
        sftper.sftp.listdir(path='/tmp/nginx_conf_bak')
    except FileNotFoundError:
        sftper.sftp.mkdir('/tmp/nginx_conf_bak')
    observer.schedule(Rsyncer(sftper, execer), path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        sftper.close()
        execer.ssh.close()
    observer.join()
