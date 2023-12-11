import willump
import threading
import json
import asyncio

class WillumpSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WillumpSingleton, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.wllp = None
        self._initialized = True

    async def get_instance(self):
        if not self.wllp:
            self.wllp = await willump.Willump.start()
        return self.wllp

    async def close(self):
        if self.wllp:
            try:
                await self.wllp.close()
            except Exception as e:
                print(f"错误了:{e}")
        self.wllp = None
        self._instance = None
        self._initialized = False 

class ThreadSingleton():
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ThreadSingleton, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.Thread = None
        self.loop_ready= threading.Event()
        self.loop = None

    def get_instance(self):
        if self.loop is None:
            with ThreadSingleton._lock:
                if self.loop is None:
                    self.Thread = threading.Thread(target=self.thread_function)
                    self.Thread.daemon = True
                    self.Thread.start()
                    self.loop_ready.wait()

        return self.loop

    def thread_function(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop_ready.set()
        self.loop.run_forever()

wllp = WillumpSingleton()
Thread = ThreadSingleton().get_instance()




