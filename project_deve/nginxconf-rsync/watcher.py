import os
import time
import logging
import paramiko
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def remote_scp_password(hostname, port, remote_path, local_path, username, password):
    t = paramiko.Transport((hostname, port))
    t.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    src = local_path
    des = remote_path
    sftp.put(src, des)
    t.close()


def remote_scp_key(hostname, port, remote_path, local_path, username, pkey_file):
    key = paramiko.RSAKey.from_private_key_file(pkey_file)
    t = paramiko.Transport((hostname, port))
    t.connect(username=username, pkey=key)
    sftp = paramiko.SFTPClient.from_transport(t)
    src = local_path
    logging.info('exec remote_scp_key fun, src is {0}'.format(src))
    des = remote_path
    logging.info('exec remote_scp_key fun, des is {0}'.format(des))
    sftp.put(src, des)
    t.close()


#def ssh_connect(hostname, port, username, password):
#    ssh = paramiko.SSHClient()
#    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#    ssh.connect(hostname, port, username, password, timeout=10)
#    return ssh


def ssh_connect_key(hostname, port, username, pkey_file):
    my_key = paramiko.RSAKey.from_private_key_file(pkey_file)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.connect(hostname, port, username, pkey=my_key, timeout=10)
    return ssh


##def exec_command(cmd):
#    s = ssh_connect(hostname, port, username, password)
#    stdin, stdout, stderr = s.exec_command(cmd)
#    cmd_result = stdout.read(), stderr.read()
#    for line in cmd_result:
#        print(line)
#    s.close()


def exec_command_connect_key(cmd):
    s = ssh_connect_key(hostname, port, username, pkey_file)
    stdin, stdout, stderr = s.exec_command(cmd)
    cmd_result = stdout.read(), stderr.read()
    for line in cmd_result:
        logging.info('exec_command_connect_key, test is successful in {0}'.format(line.decode()))
        if 'test is successful' in line.decode() and len(line.decode()) != 0:
            s.exec_command('/usr/local/nginx18/sbin/nginx -s reload')
            logging.info('exec nginx -s reload')
    s.close()


class WatcherHandler(FileSystemEventHandler):
    def __init__(self):
        self.log_event_handler = LoggingEventHandler()

    def on_created(self, event):
        """http://pythonhosted.org/watchdog/_modules/watchdog/events.html#LoggingEventHandler"""
        LoggingEventHandler.on_created(self.log_event_handler, event)
        local_path = event.src_path
        remote_path = local_path
        local_path_basename = os.path.basename(local_path)
        if os.path.isfile(local_path) and not local_path_basename.startswith('.'):
            remote_scp_key(hostname, port, remote_path, local_path, username, pkey_file)
            exec_command_connect_key('/usr/local/nginx18/sbin/nginx -t')
        if os.path.isdir(local_path):
            exec_command_connect_key('mkdir ' + remote_path)
            exec_command_connect_key('/usr/local/nginx18/sbin/nginx -t')

    def on_moved(self, event):
        LoggingEventHandler.on_moved(self.log_event_handler, event)
        src_path = event.src_path
        print(src_path)
        des_path = event.dest_path
        print(des_path)
        exec_command_connect_key('mv' + ' ' + src_path + ' ' + des_path)
        exec_command_connect_key('/usr/local/nginx18/sbin/nginx -t')

    def on_modified(self, event):
        LoggingEventHandler.on_modified(self.log_event_handler, event)
        local_path = event.src_path
        if os.path.isdir(local_path):
            pass
        local_path_basename = os.path.basename(local_path)
        if os.path.isfile(local_path) and not local_path_basename.startswith('.'):
            remote_path = local_path
            remote_scp_key(hostname, port, remote_path, local_path, username, pkey_file)
            exec_command_connect_key('/usr/local/nginx18/sbin/nginx -t')

    def on_deleted(self, event):
        LoggingEventHandler.on_deleted(self.log_event_handler, event)
        local_path = event.src_path
        remote_path = local_path
        local_path_basename = os.path.basename(local_path)
        if not local_path_basename.startswith('.'):
            exec_command_connect_key(os.path.join('rm -f ', remote_path))
            exec_command_connect_key('/usr/local/nginx18/sbin/nginx -t')
        exec_command_connect_key('rm -rf ' + remote_path)
        exec_command_connect_key('/usr/local/nginx18/sbin/nginx -t')


if __name__ == "__main__":
    hostname = '172.31.0.9'
    port = 22
    username = 'root'
    password = 'yFb&246'
    pkey_file = '/home/neal/.ssh/id_rsa'
    directory = '/usr/local/nginx18/conf/layer7'

    event_handler = WatcherHandler()
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
