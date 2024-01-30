# myApp/utils/server_utils.py

import paramiko
import docker
from confluent_kafka import Consumer
from threading import Lock
from ..shared_data import server_data
import time


def start_kafka_consumer():
    server_data_lock = Lock()

    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'server_health_check',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe(['message_queue'])

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
        server_name = msg.value().decode('utf-8')
        result = process_server_health(server_name)

        with server_data_lock:
            server_data[server_name] = result

        # Store or send this result to the frontend

        time.sleep(1)  # Adjust based on processing needs

    consumer.close()


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

def process_server_health(server):
    results = {}
    print(server_data)

    # Init SSH Connection Parameters
    hostname = 'localhost'
    username = 'remote_user'
    password = 'password1234'
    print(server)

    # for server in server_list:
    port = docker_get_host_port(server)

    # Create SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the Docker container
        client.connect(hostname, port=port, username=username, password=password)

        # Run the 'df -i' command
        # command = 'df -i; cat /etc/os-release'
        command = 'df -i'
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8')
        print(output)
        # process inode usage
        lines = output.split('\n')
        header = lines[0]
        state = 'healthy'
        unhealthy_filesystems = []

        # Skip header and interate through each filesystem.
        for line in lines[1:-1]:
        # Split each line into columns
            columns = line.split()
    
            if len(columns) >= 6:
                iuse_percentage_str = columns[4].replace('%', '')
                
                try:
                    iuse_percentage = int(iuse_percentage_str)
                    print(iuse_percentage)
                except ValueError:
                    print(f"Error: Invalid IUse% value - {iuse_percentage_str}")
                    continue
                if iuse_percentage >= 95:
                    unhealthy_filesystems.append([columns[0], columns[4]])
                    state = 'Warning'
            else:
                print("Error: Invalid 'df -i' output format")
        print(state)

        results = {
            'state': state,
            'unhealthy_filesystems': unhealthy_filesystems,
            # 'inodes': output
        }

        # output = parse_server_health_results(output)
    finally:
        # Close the SSH connection
        client.close()
        
    return results