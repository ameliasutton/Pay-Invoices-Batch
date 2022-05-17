import sys
from datetime import datetime


class logger:
    def __init__(self, fileName: str = None):
        self.start = datetime.now()
        if fileName:
            self.logfile = f"{fileName}.log"
        else:
            self.logfile = "log.log"
        print(f"Saving Log to: {self.logfile}")
        sys.stdout = open(self.logfile, "w")
        print(f"Log start time: {self.start}\n")
        self.logging = True

    def elapsedTime(self):
        return datetime.now() - self.start

    def elapsedTimeSeconds(self):
        return self.elapsedTime().seconds

    def pauseLogging(self):
        if self.logging:
            sys.stdout = sys.__stdout__
            self.logging = False

    def resumeLogging(self):
        if not self.logging:
            sys.stdout = open(self.logfile, "a")
            self.logging = True


if __name__ == "__main__":
    log = logger("test_log")
    print(log.elapsedTime())
    print(log.elapsedTimeSeconds())
    log.pauseLogging()
    print("paused")
    log.resumeLogging()
    print("resumed")
