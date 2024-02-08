import paramiko

# Init SSH Connection Parameters
hostname = 'localhost'
username = 'remote_user'
password = 'password1234'

# Timeout after 40 seconds
connection_timeout = 10

# for server in server_list:
port = 2204
if not port: 
    print("invalid port")

# Create SSH client
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connect to the Docker container
    client.connect(hostname, port=port, username=username, password=password, timeout=connection_timeout)

    # Open an interactive shell session
    shell = client.invoke_shell()

    # Send commands to the shell
    commands = [
        'sudo mkfs.ext4 -N 100 /dev/sdX',
        'sudo mkdir /mnt/test',
        'sudo mount /dev/sdX /mnt/test',
        'for i in {1..97}; do touch /mnt/test/file$i.txt; done'
    ]
    for command in commands:
        shell.send(command + '\n')

    # Wait for command execution to complete
    while not shell.recv_ready():
        pass

    # Read command output
    output = shell.recv(4096).decode('utf-8')
    print(output)
    print()

except paramiko.SSHException as e:
    print(f"SSH Error: {e}")
except paramiko.AuthenticationException as e:
    print(f"Authentication Error: {e}")
except Exception as e:
    print(f"Exception when trying to connect for server: {e}")

finally:
    # Close the SSH client
    client.close()
