# Shared data between views and server_utils
from threading import Lock

server_data = {}
server_data_lock = Lock()