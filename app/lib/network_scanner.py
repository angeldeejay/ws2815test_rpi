#!/usr/bin/env python
# ping a list of host with threads for increase speed
# design to use data from/to SQL database
# use standard linux /bin/ping utility

import time
import re
import inspect
import queue
from subprocess import Popen as call_process, PIPE
from lib.threading import Thread


class NetworkScanner:
    def __init__(self, prefix='192.168.1', timeout=60, threads=64, ips=None):
        self.prefix = prefix
        self.__running = False
        self.__threads = threads
        self.__workers = []
        self.__timeout_workers = {}
        if ips is None:
            self.__ips = [f'{self.prefix}.{str(i)}' for i in range(1, 255)]
        else:
            self.__ips = ips
        self.__queue = queue.Queue()
        self.__ttl = timeout
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
                args = ['/bin/ping', '-c', '1', '-W', '2', ip]
                ping_result = call_process(
                    args, shell=False, stdout=PIPE).wait()
                if ping_result == 0:
                    self.__notify_alive(ip)
                else:
                    self.__notify_timeout(ip)
            except:
                pass
            self.__queue.task_done()
            time.sleep(1)

    def __notify_alive(self, ip):
        if ip in self.__timeout_workers:
            try:
                self.__timeout_workers[ip].kill()
            except:
                pass

            try:
                del self.__timeout_workers[ip]
            except:
                pass

        if not ip in self.state:
            self.__log(f'{ip} found!')
        elif self.state[ip]['attempts'] >= int(round(self.__ttl / 4)):
            self.__log(f'{ip} reconnected!')

        self.state[ip] = {'up': True, 'attempts': 0}

    def __notify_timeout(self, ip):
        if ip not in self.__timeout_workers:
            self.__timeout_workers[ip] = Thread(
                target=self.__timeout_wait, args=[ip], daemon=True)
            self.__timeout_workers[ip].start()

    def __timeout_wait(self, ip):
        while True:
            if ip not in self.state:
                break
            else:
                if self.state[ip]['attempts'] == int(round(self.__ttl / 4)):
                    self.__log(f'{ip} lost. Trying to reach it...')
                self.state[ip].update(
                    {'attempts': self.state[ip]['attempts'] + 1})

                if self.state[ip]['attempts'] > self.__ttl:
                    self.__log(f'{ip} is unreachable')
                    del self.state[ip]
            time.sleep(1)

        try:
            del self.__timeout_workers[ip]
        except:
            pass

    def __process(self):
        while self.__running:
            self.__enqueue_ips()
            while not self.__queue.empty():
                time.sleep(1)

    def __enqueue_ips(self):
        for ip in self.__ips:
            self.__queue.put(ip)

    def __init_workers(self):
        self.__log("Initializing workers")
        num_threads = min(self.__threads, len(self.__ips))
        main_thread = Thread(target=self.__process, args=[], daemon=True)
        self.__workers.append(main_thread)
        for i in range(0, num_threads):
            worker = Thread(target=self.__thread_pinger, args=[i], daemon=True)
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

        for worker in self.__timeout_workers.values():
            if worker.is_alive():
                worker.kill()

        self.__log("Terminating %d workers" % len(self.__workers))

        for worker in self.__workers:
            if worker.is_alive():
                worker.kill()

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
        return ip in self.state and self.state[ip]['up'] == True

    def wait_host(self, ip):
        attempts = 0
        while attempts < 10:
            if self.is_alive(ip):
                return True
            attempts += 1
            time.sleep(1)
        return False

    def __log(self, a, sep=' => ', flush=True, end="\n"):
        print(self.__class__.__name__, a, sep=sep, flush=flush, end=end)
