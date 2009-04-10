import time
import sys, os

class Counter(object):
    def mesg(self):
        return " %s entries" % self.counter

    def __init__(self, step, console=os.isatty(1)):
        self.counter = 0
        self.steps = step
        self.console = console
        self.dots = 0

    def write(self, txt):
        if not self.console: return
        if self.dots + len(txt) >= 50:
            self.endline()
        sys.stdout.write(txt); sys.stdout.flush()
        self.dots += len(txt)

    def endline(self):
        if self.console:
            more = (50 - self.dots)
            print ' ' * more, self.mesg()
            self.dots = 0

    def dot(self):
        self.dots += 1
        if self.console:
            sys.stdout.write('.'); sys.stdout.flush()
            if self.dots >= 50:
                self.endline()
        
    def step(self):
        if self.console:
            if not self.counter % self.steps and self.counter:
                self.dot()
        self.counter += 1

    def __del__(self):
        if self.counter and self.console:
            self.endline()

class BadCounter(Counter):
    def mesg(self):
        return " %s lines, %s errors" % (self.counter, self.errors)

    def __init__(self, step):
        super(BadCounter, self).__init__(step)
        self.errors = 0

    def bad(self):
        self.errors += 1

_self_time = None
def calc_self_time():
    global _self_time
    if _self_time is None:
        tc = TimedCounter(1000, False)
        for _ in xrange(100000):
            tc.step()
        _self_time = (time.time() - tc.oldtime) / 100000
    return _self_time

class TimedCounter(Counter):
    def mesg(self):
        count = (self.counter - self.oldcounter)
        delta = time.time() - self.oldtime - count * calc_self_time()
        if delta <=0: delta = 1e-9
        lps = count / delta
        self.oldtime = time.time()
        self.oldcounter = self.counter
        return " %s lines, %s errors, %.1f lines/sec" % (self.counter, self.errors, lps)

    def __init__(self, step, console=os.isatty(1)):
        super(TimedCounter, self).__init__(step, console)
        self.errors = 0
        self.time = time.time()
        self.oldtime = self.time
        self.oldcounter = 0

    def bad(self):
        self.errors += 1
