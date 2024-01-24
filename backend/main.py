import paramiko

# SSH Connection Parameters
hostname = 'localhost'
port = 58897
username = 'remote_user'
password = 'password1234'

# Create SSH client
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connect to the Docker container
    client.connect(hostname, port=port, username=username, password=password)

    # Run the 'df -i' command
    command = 'df -i'
    stdin, stdout, stderr = client.exec_command(command)

    # Capture and print the output
    output = stdout.read().decode('utf-8')
    print(f"Output of '{command}':\n{output}")

finally:
    # Close the SSH connection
    client.close()
