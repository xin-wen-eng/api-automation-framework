#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/28 10:52
"""


import time
import threading


class PyTimer:
    """Timer class"""

    def __init__(self, func, *args, **kwargs):
        """Constructor"""

        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.running = False

    def _run_func(self):
        """Run the timed event function"""

        _thread = threading.Thread(target=self.func, args=self.args, kwargs=self.kwargs)
        _thread.setDaemon(True)
        _thread.start()

    def _start(self, interval, once):
        """Thread function to start the timer"""

        interval = max(interval, 0.01)

        if interval < 0.050:
            _dt = interval / 10
        else:
            _dt = 0.005

        if once:
            deadline = time.time() + interval
            while time.time() < deadline:
                time.sleep(_dt)

            # Timer elapsed, call the timed event function
            self._run_func()
        else:
            self.running = True
            deadline = time.time() + interval
            while self.running:
                while time.time() < deadline:
                    time.sleep(_dt)

                # Update the next timer deadline
                deadline += interval

                # Timer elapsed, call the timed event function
                if self.running:
                    self._run_func()

    def start(self, interval, once=False):
        """Start the timer

        interval    - Timer interval, float, in seconds, maximum precision 10 milliseconds
        once        - Whether to run only once, default is continuous
        """

        thread_ = threading.Thread(target=self._start, args=(interval, once))
        thread_.setDaemon(True)
        thread_.start()

    def stop(self):
        """Stop the timer"""

        self.running = False


def do_something(name, gender='male'):
    """Execute"""
    print(time.time(), 'Timer elapsed, executing specific task')
    print('name:%s, gender:%s', name, gender)
    time.sleep(5)
    print(time.time(), 'Specific task completed')


timer = PyTimer(do_something, 'Alice', gender='female')
timer.start(0.5, once=False)

input('Press Enter to exit\n')  # Block the process here
timer.stop()
