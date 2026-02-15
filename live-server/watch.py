from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

last_modified = {}
debounce_time = 0.2

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, files_to_watch, callback):
        super().__init__()
        self.files_to_watch = files_to_watch
        self.callback = callback

    def on_modified(self, event):
        filename = event.src_path
        filename = os.path.basename(filename)
        if not filename.endswith(".html"):
            return
        
        now = time.time()
        if filename in last_modified and now - last_modified[filename] < debounce_time:
            return

        last_modified[filename] = now
        self.callback(filename)

def start_watcher(files, callback):
    handler = FileChangeHandler(files, callback)
    observer = Observer()
    observer.schedule(handler, path=".", recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except:
        observer.stop()
    observer.join()
