# myApp/utils/server_utils.py

import paramiko
import docker
from confluent_kafka import Consumer
from threading import Lock
from ..shared_data import server_data, server_data_lock
from concurrent.futures import ThreadPoolExecutor
import time
import logging
from threading import current_thread
from django.core.cache import cache
import json
from django.core.cache import cache

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(threadName)s] %(message)s')
logger = logging.getLogger(__name__)

def get_server_data(server_name):
    data = cache.get(server_name)
    return json.loads(data) if data else {}

def process_server_health_thread(server_name, connection_id):
    try:
        print(f"Starting health check for {server_name}")
        # Simulate the health check process
        # result = {"status": "Healthy", "last_updated": time.time()}
        result = process_server_health(server_name)
        data = {
            'server_name': server_name,
            'status': result,
            'last_updated': time.time(),
        }

        cache_key = connection_id + "-" + server_name
        # Update server_data in Redis
        cache.set(cache_key, data, timeout=None)
        print(f"Completed health check for {server_name}: {result}")
    except Exception as e:
        print(f"Exception in process_server_health_thread for {server_name}: {e}")


def start_kafka_consumer():
    '''
    Kafka consumer polls for messages from the message_queue topic.
    '''
    executor = ThreadPoolExecutor(max_workers=10)
    print("Starting Kafka Consumer")

    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'server_health_check',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe(['message_queue'])
    
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            # Decode the message value from bytes to string, then load it as JSON
            message_data = json.loads(msg.value().decode('utf-8'))
            connection_id = message_data['connection_id']
            server_name = message_data['server']

            # This is called for every server name (message) received
            # This submits the process_server_health_thread function 
            # to a thread in the ThreadPoolExecutor for asynchronous execution
            executor.submit(process_server_health_thread, server_name, connection_id)

    except Exception as e:
        print(f"Error in Kafka consumer thread: {e}")
    finally:
        consumer.close()
        executor.shutdown()

def docker_get_host_port(container_name):
    '''
    Since I am using a bunch of docker containers to simulate having several Linux servers on
    my network, I need this function to ask docker what port that specific container resides
    on. This is more for dev purposes.
    '''
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
        return None

def parse_operating_system_info(os_output):
    os_pretty_name = ''
    for line in os_output.split('\n'):
        if line.startswith('PRETTY_NAME'):
            os_pretty_name = line.split('=')[1].strip('"')
            break
    return os_pretty_name


def parse_inode_health_results(inode_output):
    lines = inode_output.strip().split('\n')
    state = 'Healthy'
    parsed = []
    unhealthy_filesystems = []
    unhealthy_filesystems.append(lines[0])
    for line in lines[1:]:
        parts = line.split()
        filesystem = parts[0]
        iuse = int(parts[4][:-1])
        if iuse >= 3:
            unhealthy_filesystems.append(line)
            state = 'Warning'

        parsed.append((filesystem, iuse))
    
    return (state, unhealthy_filesystems, inode_output)

def parse_filesystem_health_results(filesystem_output):
    print(filesystem_output)
    lines = filesystem_output[1].split('\n')
    print(lines)
    state = 'Healthy'
    unhealthy_filesystems = []

    # Skip header and interate through each filesystem.
    for line in lines[1:-1]:
    # Split each line into columns
        columns = line.split()

        if len(columns) >= 6:
            fuse_percentage_str = columns[4].replace('%', '')
            
            try:
                iuse_percentage = int(fuse_percentage_str)
            except ValueError:
                print(f"Error: Invalid FUse% value - {fuse_percentage_str}")
                continue
            if iuse_percentage >= 5:
                print("WARNING")
                unhealthy_filesystems.append([columns[0], columns[4]])
                state = 'Warning'
        else:
            print("Error: Invalid 'df -h' output format")
    
    return (state, unhealthy_filesystems, filesystem_output)

def parse_server_health_results(outputs):
    # Parsing logic will go here
    results = {}

    # parse OS info
    os_verion = parse_operating_system_info(outputs[0])
    # parse inode health
    inode_health_results = parse_inode_health_results(outputs[1])
    # parse filesystem health
    filesystem_health_results = parse_filesystem_health_results(outputs[2])

    overall_health = 'Healthy'
    if inode_health_results[0] != 'Healthy':
        overall_health = 'Warning'

    results = {
        'overall_state': overall_health,
        'os_info': {
            'operating_system_name': os_verion,
        },
        'inode_info': {
            'inode_health_status': inode_health_results[0],
            'unhealthy_filesystems': inode_health_results[1],
            'inode_data': inode_health_results[2],
        },
        'filesystem_info': {
            'filesystem_health_status': filesystem_health_results[0],
            'unhealthy_filesystems': filesystem_health_results[1],
            'filesystem_data': filesystem_health_results[2],
        },
        'ntp_info': {
            'ntp_health_status': '',
        },
    }

    return results

def process_server_health(server):
    print("Starting the health check processing:")

    # Init SSH Connection Parameters
    hostname = 'localhost'
    username = 'remote_user'
    password = 'password1234'
    
    # Timeout after 40 seconds
    connection_timeout = 10

    print(server)

    # for server in server_list:
    port = docker_get_host_port(server)
    if not port: 

        return {
            'overall_state': 'Error',
            'os_info': {
                'operating_system_name': 'N/A',
            },
            'inode_info': {
                'inode_health_status': 'N/A',
                'unhealthy_filesystems': 'N/A',
                'inode_data': 'N/A',
            },
            'filesystem_info': {
                'filesystem_health_status': 'N/A',
                'unhealthy_filesystems': 'N/A',
                'filesystem_data': 'N/A',
            },
            'ntp_info': {
                'ntp_health_status': 'N/A',
            },
        }
    # Create SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the Docker container
        client.connect(hostname, port=port, username=username, password=password, timeout=connection_timeout)

        # Run the 'df -i' command
        # command = 'df -i; cat /etc/os-release'
        # command = 'df -i'
        commands = (
            'cat /etc/os-release',
            'df -i',
            'df -h',
        )
        delimiter = "END_OF_COMMAND_OUTPUT"
        command = '; echo "{}"; '.format(delimiter).join(commands) + '; echo "{}"'.format(delimiter)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8')


        # Split output with delimiter to get a list of command outputs
        # outputs[1] = inodes
        # outputs[2] = filesystems
        outputs = output.split(delimiter)
        # Strip each output to remove leading + trailing whitespace
        outputs = [o.strip() for o in outputs if o.strip()]

        # parse output
        results = parse_server_health_results(outputs)
    except Exception as e:
        print(f"Exception in when trying to connect for {server_name}: {e}")

        results = {
            'overall_state': 'Error',
        }
    
    finally:
        # Close the SSH connection
        client.close()
        
    return results