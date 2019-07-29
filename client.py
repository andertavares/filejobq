import os.path
import time
from pathlib import Path
import subprocess

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


    def run(self):

        while True:


            # skips if the directory is locked
            if os.path.exists(self.lock_file):
                time.sleep(1)
                continue

            # if job is currently running, checks if it has finished
            if self.job is not None:
                if self.job.poll() is not None: # terminated!
                    self.mark_finished()
                    self.job = None
                    self.job_command = None
                else: # job is running, wait a bit
                    time.sleep(1)
                    continue

            # looks for a job
            else:
                self.job = self.find_job()



    def find_job(self):

        self.lock()


        subprocess.Popen(
            './rlexperiment.sh -c %s -o %s/rep%s %s' \
            % (experiment_config, output_prefix, str(total_runs).zfill(2), additional_args),
            shell=True
        )

        self.unlock()


    def mark_finished(self):

        self.lock()

        read_handler = open(self.in_progress, 'r')

        # removes the command in doing.txt
        running = [line.trim() for line in read_handler.readlines()]
        running.remove(self.job_command)
        read_handler.close()

        rewrite_handler = open(self.in_progress, 'w')
        rewrite_handler.writelines(running)
        rewrite_handler.close()

        self.unlock()

    def lock(self):
        while os.path.exists(self.lock_file): # waits until the directory is free
            time.sleep(1)
            continue

        # locks the dir
        Path(self.lock_file).touch()

    def unlock(self):
        os.remove(self.lock_file)



