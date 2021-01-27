#!/usr/bin/env python
# ping a list of host with threads for increase speed
# design to use data from/to SQL database
# use standard linux /bin/ping utility

import threading
import time
import re
import inspect
import queue
from subprocess import Popen as call_process, PIPE
from threading import *


class NetworkScanner:
    def __init__(self, prefix='192.168.1', timeout=1, threads=64):
        self.prefix = prefix
        self.timeout = timeout
        self.__running = False
        self.__threads = threads
        self.__workers = []
        self.__queue = queue.Queue()
        self.__ttl = 5 # 1 minute
        # self.__ttl = 60 # 1 minute
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
                ip = self.__queue.get()
                args = ['/bin/ping', '-c', '1', '-W',
                        str(round(int(round(self.timeout, 0)) * 0.75, 2)), ip]

                ping_result = call_process(args, shell=False, stdout=PIPE).wait()
                if ping_result == 0:
                    if not ip in self.state:
                        self.__log(f'{ip} found!')
                    elif self.state[ip]['attempts'] >= 2:
                        self.__log(f'{ip} reconnected!')
                    self.state[ip] = {'up': True, 'attempts': 0}
                else:
                    if ip in self.state:
                        if self.state[ip]['up'] == True:
                            if self.state[ip]['attempts'] < self.__ttl:
                                if self.state[ip]['attempts'] == 2:
                                    self.__log(f'Lost connection with {ip}. Trying to reach it...')
                                self.state[ip] = {'up': self.state[ip]['up'], 'attempts': self.state[ip]['attempts'] + 1}
                            else:
                                self.__log(f'{ip} is unreachable')
                                del self.state[ip]
                        else:
                            self.__log(f'{ip} is unreachable')
                            del self.state[ip]
            except:
                pass
            self.__queue.task_done()

    def __process(self):
        while self.__running:
            self.__enqueue_ips()
            while not self.__queue.empty():
                time.sleep(0.01)

    def __enqueue_ips(self):
        for ip in [f'{self.prefix}.{str(i)}' for i in range(1, 255)]:
            self.__queue.put(ip)

    def __init_workers(self):
        self.__log("Initializing workers")
        main_thread = Thread(target=self.__process, args=[])
        main_thread.setDaemon(True)
        self.__workers.append(main_thread)
        for i in range(0, self.__threads):
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
        self.__log("Dequeue %s" % str(self.__queue))
        with self.__queue.mutex:
            self.__queue.queue.clear()

        self.__log("Terminating %d workers" % len(self.__workers))
        for worker in self.__workers:
            if worker.is_alive():
                worker.join(0)

        self.__log("%s workers terminated" % len(self.__workers))
        self.__workers = []
        self.__log("Stopped")

    def start(self):
        if self.__running:
            return

        self.__log("Starting")
        self.__running = True
        self.__init_workers()
        self.__start_workers()

    def is_alive(self, ip):
        # self.__log(self.state)
        try:
            is_alive = self.state[ip]['up']
            return is_alive
        except Exception as e:
            pass
        return False

    def wait_host(self, ip):
        attempts = 0
        while attempts < 10:
            if self.is_alive(ip):
                return True
            attempts += 1
            time.sleep(1)
        return False

    def __log(self, a):
        print(self.__class__.__name__, a, sep=' => ', flush=True)
