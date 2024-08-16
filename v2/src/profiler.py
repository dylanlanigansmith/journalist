import time
from colorama import Fore, Back, Style


class Profiler:
    def __init__(self, name):
        self.start_time = time.time()
        self.name = name
    def elapsed(self):
        return time.time() - self.start_time
    def reset(self):
        self.start_time = time.time()
        return self.start_time

    def end(self):
        total = self.elapsed()
        print(f"{Back.WHITE}{Fore.BLACK} '{self.name}' complete in {total:.4f}s  {Style.RESET_ALL}")
        return total
    def start(self):
        self.reset()
    def stop(self):
        self.end()