import os
import time
import threading
import logging
import paramiko
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s [%(threadName)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='multiHostSyncFile.log',
                    filemode='a'
                    )


class Sftper(object):
    def __init__(self, host, port, username, key_file):
        self.key = paramiko.RSAKey.from_private_key_file(key_file)
        self.t = paramiko.Transport((host, port))
        self.t.connect(username=username, pkey=self.key)
        self.sftp = paramiko.SFTPClient.from_transport(self.t)
        self.host = host

    def put(self, src_path, dest_path):
        logging.info('Thread {0} is running...'.format(threading.current_thread().name))
        logging.info('Copy {0} to {1}'.format(src_path, self.host))
        self.sftp.put(src_path, dest_path)

    def close(self):
        self.sftp.close()


class Executor(object):
    def __init__(self, host, port, username, key_file):
        self.host = host
        self.key = paramiko.RSAKey.from_private_key_file(key_file)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.load_system_host_keys()
        self.ssh.connect(host, port, username, pkey=self.key, timeout=10)

    def exec(self, cmd):
        logging.info('Thread [{0}] is running...'.format(threading.current_thread().name))
        logging.info('Execute [{0}] will be {1}'.format(cmd, host))
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        cmd_result = stdout.read(), stderr.read()
        for line in cmd_result:
            logging.info('Command execution output: {0}'.format(line.decode()))

    def syntax_check(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        cmd_result = stdout.read(), stderr.read()   # cmd_result is a tuple
        for line in cmd_result:
            if 'test is successful' in line.decode():
                logging.info('Syntax is ok for {0}, reload nginx config'.format(self.host))
                self.ssh.exec_command('/usr/local/nginx18/sbin/nginx -s reload')


def loop_exec(hosts, cmd):
    for host in hosts:
        t = threading.Thread(target=exec_dict[host].exec, args=(cmd, ), name='Thread-loop_exec-fun' + '-' + host)
        t.daemon = True
        t.start()
        t.join(timeout=2)
        if os.listdir(os.path.join(path, 'layer7')):
            exec_dict[host].syntax_check('/usr/local/nginx18/sbin/nginx -t')
        else:
            logging.warning(os.path.join(path, 'layer7') + ' is empty!')


def loop_copyfile(hosts, src_path, dest_path):
    for host in hosts:
        t = threading.Thread(target=sftp_dict[host].put, args=(src_path, dest_path,), name='Thread-' + host)
        t.daemon = True
        t.start()
        t.join(timeout=2)
        exec_dict[host].syntax_check('/usr/local/nginx18/sbin/nginx -t')


class FileMonitor(FileSystemEventHandler):
    def __init__(self, hosts ):
        self.hosts = hosts

    def on_created(self, event):
        if os.path.isdir(event.src_path):
            cmd = 'mkdir ' + '-pv ' + event.src_path
            loop_exec(self.hosts, cmd)
        if os.path.isfile(event.src_path):
            if not os.path.basename(event.src_path).startswith('.') \
                    and not os.path.basename(event.src_path).endswith('~')\
                    and not os.path.basename(event.src_path).startswith('sed'):
                logging.info('Create {0}, scp to {1}'.format(event.src_path, self.hosts))
                loop_copyfile(self.hosts, event.src_path, event.src_path)

    def on_modified(self, event):
        if os.path.isdir(event.src_path):
            logging.info('Modify the directory, will be ignored {0}'.format(event.src_path))
        if os.path.isfile(event.src_path) and not os.path.basename(event.src_path).endswith('.swp'):
            logging.info('Modify the file {0}, will be ignored'.format(event.src_path))
            # 修改一个文件,watchdog也监控是创建一个文件,此处可不做处理

    def on_moved(self, event):
        if not os.path.basename(event.dest_path).endswith('~') and not os.path.basename(event.src_path).startswith('sed'):
            cmd = 'mv' + ' ' + event.src_path + ' ' + event.dest_path
            logging.info('Move {0} to {1} on {2}'.format(event.src_path, event.dest_path, self.hosts))
            loop_exec(self.hosts, cmd)
        if os.path.basename(event.src_path).startswith('sed'):
            """当用sed命令来修改文件时，sed会把原文件copy成一个以sed开头的文件，修改结束后会把这个文件重命令为原文件名"""
            logging.info('user sed commmand modify confige, {0} will be scp to remote host'.format(event.dest_path))
            loop_copyfile(self.hosts, event.dest_path, event.dest_path)

    def on_deleted(self, event):
        if not os.path.basename(event.src_path).endswith('~') \
                and not os.path.basename(event.src_path).endswith('.swp') \
                and not os.path.basename(event.src_path).endswith('.swx') \
                and not os.path.basename(event.src_path).endswith('.swpx') \
                and not os.path.basename(event.src_path).isdigit():
            logging.info('Delete file {0}, will move {0} to /tmp/nginx_conf_bak'.format(event.src_path))
            cmd = 'mv' + ' ' + event.src_path + ' ' + '/tmp/nginx_conf_bak/' + os.path.basename(event.src_path) + '-' + str(time.time())
            loop_exec(self.hosts, cmd)


if __name__ == '__main__':
    hosts = ['172.31.0.9']
    port = 22
    username = 'root'
    key_file = '/home/neal/.ssh/id_rsa'
    path = '/usr/local/nginx18/conf'

    """为了节约网络socket,在脚本运行上就初始好各个ip的Sftper对象"""
    sftp_dict = {}
    for host in hosts:
        sftp_dict[host] = Sftper(host, port, username, key_file)
    #logging.info(sftp_dict)
    exec_dict = {}
    for host in hosts:
        exec_dict[host] = Executor(host, port, username, key_file)
    #logging.info(exec_dict)
    for host in hosts:
        try:
            sftp_dict[host].sftp.listdir(path='/tmp/nginx_conf_bak')
        except FileNotFoundError:
            sftp_dict[host].sftp.mkdir('/tmp/nginx_conf_bak')

    observer = Observer()
    observer.schedule(FileMonitor(hosts), path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
