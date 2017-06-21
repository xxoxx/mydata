import paramiko


def ssh_connect(hostname, port, username, password, cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password, timeout=5)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    cmd_result = stdout.read(), stderr.read()
    for line in cmd_result:
        if 'test is successful' in line.decode():
            print('test')
        print(line.decode())
    ssh.close()


def ssh_connect_key(hostname, port, username, key_file, cmd):
    key = paramiko.RSAKey.from_private_key_file(key_file)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.connect(hostname, port, username, pkey=key, timeout=5)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    cmd_result = stdout.read(), stderr.read()
    for line in cmd_result:
        print(line)
    ssh.close()


if __name__ == '__main__':
    #ssh_connect('172.31.0.9', 22, 'root', 'yFb&246', '/usr/local/nginx18/sbin/nginx -t')
    key_file = '/home/ansible/.ssh/id_rsa'
    ssh_connect_key(hostname='172.31.0.9', port=22, username='root', key_file, 'hostname')
