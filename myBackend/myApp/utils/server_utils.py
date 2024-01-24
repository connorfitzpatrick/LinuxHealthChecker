# myApp/utils/server_utils.py

import paramiko
import docker

def docker_get_host_port(container_name):
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        ports = container.attrs['NetworkSettings']['Ports']
        for container_port, host_ports in ports.items():
            if host_ports:
                host_port = host_ports[0]['HostPort']
                print(f"  Container Port {container_port}/tcp is mapped to Host Port {host_port}")
                return host_port
            else:
                print(f"  Container Port {container_port}/tcp is not mapped to any Host Port")

    except docker.errors.NotFound:
        print(f"Container '{container_name}' not found.")

def parse_server_health_results(results):
    parsed_results = {}
    # Parsing logic will go here
    return parsed_results

def process_servers_health(server_list):
    results = {}

    # Init SSH Connection Parameters
    hostname = 'localhost'
    port = -1
    username = 'remote_user'
    password = 'password1234'
    print(server_list)

    for server in server_list:
        port = docker_get_host_port(server)

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

            # output = parse_server_health_results(output)
        finally:
            # Close the SSH connection
            client.close()