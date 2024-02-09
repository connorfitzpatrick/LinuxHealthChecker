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
    # try:
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
    # except Exception as e:
    #     print(f"Exception in process_server_health_thread for {server_name}: {e}")


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


def parse_inode_health_results(inode_output, server_name):
    lines = inode_output.strip().split('\n')
    state = 'Healthy'
    data = []
    issues = []
    for line in lines[1:]:
        parts = line.split()
        if server_name == "abcdefgh004" and parts[0] == "shm":
            parts[4] = "96%"
        inode_entry = {
            'Filesystem': parts[0],
            'Size': parts[1],
            'Used': parts[2],
            'Avail': parts[3],
            'Use%': parts[4],
            'MountedOn': parts[5],
        }
        if int(parts[4][:-1]) >= 95:
            state = 'Warning'
            issues.append("Inode usage in " + parts[0] + " is currently at " + parts[4])
        data.append(inode_entry)
    
    return (state, issues, data)

def parse_filesystem_health_results(filesystem_output, server_name):
    lines = filesystem_output.strip().split('\n')
    state = 'Healthy'
    data = []
    issues = []

    for line in lines[1:]:
        parts = line.split()
        if server_name == "abcdefgh004" and parts[0] == "/dev/vda1":
            parts[4] = "96%"
        filesystem_entry = {
            'Filesystem': parts[0],
            'Size': parts[1],
            'Used': parts[2],
            'Avail': parts[3],
            'Use%': parts[4],
            'MountedOn': parts[5],
        }
        if int(parts[4][:-1]) >= 95:
            state = 'Warning'
            issues.append("Filesystem usage in " + parts[0] + " is currently at " + parts[4])
        data.append(filesystem_entry)

    return (state, issues, data)

def parse_server_logs(log_output):
    lines = log_output.strip().split('\n')
    return lines

def parse_server_health_results(outputs, server_name):
    # Parsing logic will go here
    results = {}
    # Warning messages will go here
    server_issues = {}

    # parse OS info
    os_verion = parse_operating_system_info(outputs[0])
    # parse inode health
    inode_health_results = parse_inode_health_results(outputs[1], server_name)
    # parse filesystem health
    filesystem_health_results = parse_filesystem_health_results(outputs[2], server_name)

    overall_health = 'Healthy'
    if inode_health_results[0] != 'Healthy':
        overall_health = 'Warning'
        # server_issues['Inodes'].extend(inode_health_results[1])
        server_issues['Inodes'] = inode_health_results[1]
    if filesystem_health_results[0] != 'Healthy':
        overall_health = 'Warning'
        # server_issues['Filesystems'].extend(filesystem_health_results[1])
        server_issues['Filesystems'] = filesystem_health_results[1]


    results = {
        'overall_state': overall_health,
        'ping_status': 'Healthy',
        'os_info': {
            'operating_system_name': os_verion,
        },
        'inode_info': {
            'inode_health_status': inode_health_results[0],
            'inode_issues': inode_health_results[1],
            'inode_data': inode_health_results[2],
        },
        'filesystem_info': {
            'filesystem_health_status': filesystem_health_results[0],
            'filesystem_issues': filesystem_health_results[1],
            'filesystem_data': filesystem_health_results[2],
        },
        'ntp_info': {
            'ntp_health_status': '',
        },
        'server_issues': server_issues,
        'logs': parse_server_logs(outputs[3]),
    }

    return results

def process_server_health(server_name):
    print("Starting the health check processing:")

    # Init SSH Connection Parameters
    hostname = 'localhost'
    username = 'remote_user'
    password = 'password1234'
    
    # Timeout after 40 seconds
    connection_timeout = 10

    # for server in server_list:
    port = docker_get_host_port(server_name)
    if not port: 

        return {
            'overall_state': 'Error',
            'ping_status': 'Error',
            'os_info': {
                'operating_system_name': '',
            },
            'inode_info': {
                'inode_health_status': '',
                'inode_issues': '',
                'inode_data': '',
            },
            'filesystem_info': {
                'filesystem_health_status': '',
                'filesystem_issues': '',
                'filesystem_data': [],
            },
            'ntp_info': {
                'ntp_health_status': '',
            },
            'server_issues': {},
            'logs': [],
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
            'tail -n 70 /var/log/dpkg.log'

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
        results = parse_server_health_results(outputs, server_name)
    except Exception as e:
        print(f"Exception in when trying to connect for {server_name}: {e}")

        results = {
            'overall_state': 'Error',
        }
    
    finally:
        # Close the SSH connection
        client.close()
        
    return results