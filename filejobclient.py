#!/usr/bin/python3

import os.path
import time
import argparse
from pathlib import Path
import subprocess
from contextlib import contextmanager
from datetime import datetime, timedelta


class Client(object):

    def __init__(self, basedir):
        self.job_command = None
        self.job = None
        self.basedir = basedir

        # file names
        self.todo = os.path.join(basedir, "todo.txt")
        self.in_progress = os.path.join(basedir, "doing.txt")
        self.done = os.path.join(basedir, "done.txt")
        self.lock_file = os.path.join(basedir, ".lock")

        self.attempts = 0
        self.finished_jobs = 0

    def run(self, max_jobs=0):

        while True:
            # if I have finished as many jobs as I want, halt.
            if 0 < max_jobs <= self.finished_jobs:
                print('Finished the pre-set number of jobs (%d). Halting.' % max_jobs)
                return

            # if job is currently running, checks if it has finished
            if self.job is not None:
                if self.job.poll() is not None: # terminated!
                    self.mark_finished()

                else:  # job is running, wait a bit
                    time.sleep(1)
                    continue

            # looks for a job
            else:
                self.find_job()

                if self.job is None:  # job not found, see if max attempts was reached
                    self.attempts += 1

                    if self.attempts >= 5:
                        print("Halting after 5 unsuccessful attempts to find a job. ")
                        return

                    else:
                        print("No job found (attempt #%d). Sleeping for 5 seconds..." % self.attempts)
                        time.sleep(5)

                else:  # job found, resets the attempt counter
                    self.attempts = 0

    def find_job(self):
        with self.lock():

            # grabs a job
            todo_handler = open(self.todo, 'r')
            first_line = todo_handler.readline(4096).strip()
            if first_line is not None and first_line != '':

                # there's a valid job in the file, retrieves and runs it
                self.job_command = first_line

                print("Starting job '%s'" % self.job_command)

                # grabs the job, starts it and returns it
                self.job = subprocess.Popen(
                    self.job_command,
                    shell=True
                )

            todo_handler.close()
            if self.job is not None:  # if I found a job, move it to in progress
                self.move(self.job_command, self.todo, self.in_progress)

    def mark_finished(self):

        print("Job '%s' finished." % self.job_command)
        with self.lock():
            self.move(self.job_command, self.in_progress, self.done)

        # updates my statistics
        self.job = None
        self.job_command = None
        self.finished_jobs += 1

    # moves a line from file1 to file2
    def move(self, line_to_move, file_name1, file_name2):

        # removes the line in file1 (opens, removes, rewrites)
        read_handler = open(file_name1, 'r')
        to_remove = [line.strip() for line in read_handler.readlines()]
        to_remove.remove(line_to_move)
        read_handler.close()

        rewrite_handler = open(file_name1, 'w')
        rewrite_handler.writelines(['%s\n' % line for line in to_remove])
        rewrite_handler.close()

        # appends the line to file2
        file2_handler = open(file_name2, 'a')
        file2_handler.write('%s\n' % line_to_move)

    def lock(self, timeout=None, retry_time=0.5):

        if timeout is not None:
            deadline = datetime.now() + timedelta(seconds=timeout)

        while True:
            try:
                fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL)
                break
            except FileExistsError:
                if timeout is not None and datetime.now() >= deadline:
                    raise
                print('Directory %s is locked, will retry on %.2f seconds' % (self.basedir, retry_time))
                time.sleep(retry_time)

        yield  # lock acquired, let the user do whatever it needs to do

        try:  # user has finished: unlock
            os.close(fd)
        finally:
            os.unlink(self.lock_file)


        '''while os.path.exists(self.lock_file): # waits until the directory is free
            print("Directory is locked. ")
            time.sleep(1)
            continue
        
        # locks the dir
        Path(self.lock_file).touch()'''


    def unlock(self):
        os.remove(self.lock_file)

    '''@contextmanager
    def exclusive_open(self, filename, *args, timeout=None, retry_time=0.5, **kwargs):
        """Open a file with exclusive access across multiple processes.
        Requires write access to the directory containing the file.
        (source=https://codereview.stackexchange.com/a/150237)

        Arguments are the same as the built-in open, except for two
        additional keyword arguments:

        timeout -- Seconds to wait before giving up (or None to retry indefinitely).
        retry_time -- Seconds to wait before retrying the lock.

        Returns a context manager that closes the file and releases the lock.

        """
        if timeout is not None:
            deadline = datetime.now() + timedelta(seconds=timeout)

        while True:
            try:
                fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL)
                break
            except FileExistsError:
                if timeout is not None and datetime.now() >= deadline:
                    raise
                time.sleep(retry_time)

        try:
            with open(filename, *args, **kwargs) as f:
                yield f
        finally:
            try:
                os.close(fd)
            finally:
                os.unlink(self.lock_file)
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Simple file-based job client.'
    )

    parser.add_argument(
        'basedir',
        help='Base directory where job list are stored (as a txt file with one command per line)',
    )

    parser.add_argument(
        '-m', '--max_jobs', type=int,
        default=0,
        help='Maximum number of jobs this client will perform (0=unlimited).',
    )

    print("Starting simple file job client.")

    args = parser.parse_args()
    client = Client(args.basedir)
    client.run(args.max_jobs)
    print("Goodbye.")
