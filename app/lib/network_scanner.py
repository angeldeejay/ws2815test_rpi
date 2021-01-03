#!/usr/bin/env python
# ping a list of host with threads for increase speed
# design to use data from/to SQL database
# use standard linux /bin/ping utility

import threading
import time
import re
import inspect
import ctypes
import queue
from subprocess import Popen as call_process, PIPE


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(tid), ctypes.py_object(exctype)
    )
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class Thread(threading.Thread):
    def _get_my_tid(self):
        """determines this (self's) thread id"""
        if not self.is_alive():
            raise threading.ThreadError("the thread is not active")

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        active_threads = threading._active.copy()
        for thread_id, thread_object in active_threads.items():
            if thread_object is self:
                self._thread_id = thread_id
                return thread_id

        raise AssertionError("could not determine the thread's id")

    def __repr__(self):
        return f'@{self.__class__.__name__}'

    def raise_exc(self, exctype):
        """raises the given exception type in the context of this thread"""
        _async_raise(self._get_my_tid(), exctype)

    def terminate(self):
        """raises SystemExit in the context of the given thread, which should 
        cause the thread to exit silently (unless caught)"""
        self.raise_exc(SystemExit)


class NetworkScanner:
    def __init__(self, prefix='192.168.1', timeout=0.5):
        self.prefix = prefix
        self.timeout = timeout
        self.__running = False
        self.__workers = []
        self.__in_queue = queue.Queue()
        self.__out_queue = queue.Queue()
        self.state = {}
        self.start()

    def __repr__(self):
        return f'@{self.__class__.__name__}'

    def __thread_pinger(self, i):
        """Pings hosts in queue"""
        while True:
            if not self.__running:
                break
            try:
                (ip, ip_status) = self.__in_queue.get()

                ping_result = False
                try:
                    args = ['/bin/ping', '-c', '1', '-W',
                            str(self.timeout), ip]
                    p_ping = call_process(args, shell=False, stdout=PIPE)
                    ping_result = (p_ping.wait() == 0)
                except:
                    pass

                if ping_result:
                    ip_status['attempts'] = 0
                    ip_status['up'] = ping_result
                    # self.__log(str(p_ping.communicate()))
                else:
                    if ip_status['up']:
                        if ip_status['attempts'] < 10:
                            ip_status['attempts'] += 1
                        else:
                            ip_status['attempts'] = 0
                            ip_status['up'] = ping_result
                    else:
                        ip_status['attempts'] = 0
                        ip_status['up'] = ping_result
                self.state[ip] = ip_status
                self.__in_queue.put((ip, ip_status))
                self.__in_queue.task_done()
            except Exception as e:
                self.__log(e)
                pass
            time.sleep(0.1)

    def __process(self):
        for (ip, ip_status) in self.state.items():
            self.__in_queue.put((ip, ip_status))
        self.__in_queue.join()

        while True:
            if not self.__running:
                break
            time.sleep(0.1)

    def __init_status(self):
        for ip in [f'{self.prefix}.{str(i)}' for i in [13, 20, 151, 203]]:
            self.state[ip] = {'up': False, 'attempts': 0}

    def __init_workers(self):
        main_thread = Thread(target=self.__process, args=[])
        main_thread.setDaemon(True)
        self.__workers.append(main_thread)
        for i in range(len(self.state)):
            worker = Thread(target=self.__thread_pinger, args=[i])
            worker.setDaemon(True)
            self.__workers.append(worker)

    def __start_workers(self):
        self.__log("Starting %d workers" % len(self.__workers))
        for worker in self.__workers:
            worker.start()
            # self.__log("%s started" % str(worker))

    def stop(self):
        self.__log("Stopping...")
        self.__running = False
        for q in [self.__in_queue, self.__out_queue]:
            self.__log("Dequeue %s" % str(q))
            with q.mutex:
                q.queue.clear()

        self.__log("Terminating %d workers" % len(self.__workers))
        for worker in self.__workers:
            if worker.is_alive():
                worker.terminate()
                worker.join(0)
                worker.is_alive()
                # self.__log("%s terminated" % str(worker))

        self.__workers = []
        self.__log("Stopped")

    def start(self):
        if self.__running:
            return

        self.__log("Starting")
        self.__running = True
        self.__log("Initializing status")
        self.__init_status()
        self.__log("Initializing workers")
        self.__init_workers()
        self.__log("Starting workers")
        self.__start_workers()
        self.__log("Started")

    def is_alive(self, ip):
        try:
            is_alive = self.state[ip]['up']
            return is_alive
        except Exception as e:
            self.__log(e)
            pass
        return False

    def __log(self, a):
        print(self.__class__.__name__, a, sep=' => ', flush=True)


scanner = NetworkScanner()
while True:
    print(scanner.is_alive('192.168.1.13'))
    time.sleep(1)