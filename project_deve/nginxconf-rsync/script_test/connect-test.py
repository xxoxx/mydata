import paramiko


#ssh = paramiko.SSHClient()
#ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#ssh.connect(hostname='172.31.0.9', port=22, username='root', key_filename='/home/neal/.ssh/id_rsa')


t = paramiko.Transport(('172.31.0.9', 22))
#t.connect(username='root', pkey=paramiko.RSAKey.from_private_key_file('/home/neal/.ssh/id_rsa'))
t.connect(username='root', password='yFb&246')
sftp = paramiko.SFTPClient.from_transport(t)
sftp.put('/tmp/2.txt', '/tmp/3.txt')
sftp.get('/tmp/3.txt', '/tmp/33.txt')
print(sftp.listdir('/tmp'))
print(sftp.rename('/tmp/3.txt', '/tmp/33.txt'))

