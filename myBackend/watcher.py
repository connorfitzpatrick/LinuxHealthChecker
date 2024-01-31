import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CodeChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory or not event.src_path.endswith('.py'):
            return

        print(f'Restarting Django server due to change in {event.src_path}')
        os.system('touch /path/to/your/project/manage.py')  # Trigger a server restart by touching manage.py

def main():
    path = './'
    event_handler = CodeChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
