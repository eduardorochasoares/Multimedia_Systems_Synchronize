import paramiko
from scp import SCPClient
def transferApp(server_ip, user, passw, root_path):

    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server_ip, username=user, password=passw)

    with SCPClient(ssh.get_transport()) as scp:
        print("Transferring NCL Application...")
        scp.put(root_path+'nclapp', recursive=True,  remote_path='/misc/ncl30/')


    '''starting app'''
    stdin, stdout, stderr = ssh.exec_command('/misc/launcher.sh /misc/ncl30/nclapp/main.ncl')
    ssh.close()
