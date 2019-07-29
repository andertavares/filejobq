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

        # grabs a job
        todo_handler = open(self.todo, 'r')
        if todo_handler.readline(4096) is None or todo_handler.readline() == '':
            todo_handler.close()
            return None # no job in file

        # grabs the job, starts it and returns it
        subprocess.Popen(
            './rlexperiment.sh -c %s -o %s/rep%s %s' \
            % (experiment_config, output_prefix, str(total_runs).zfill(2), additional_args),
            shell=True
        )

        self.unlock()

    def mark_finished(self):

        self.lock()

        self.move(self.job_command, self.in_progress, self.done)

        self.unlock()

    # moves a line from file1 to file2
    def move(self, line_to_move, file_name1, file_name2):

        # removes the line in file1 (opens, removes, rewrites)
        read_handler = open(file_name1, 'r')
        to_remove = [line.trim() for line in read_handler.readlines()]
        to_remove.remove(line_to_move)
        read_handler.close()

        rewrite_handler = open(file_name1, 'w')
        rewrite_handler.writelines(line_to_move)
        rewrite_handler.close()

        # appends the line to file2
        file2_handler = open(file_name2, 'a')
        file2_handler.writelines([line_to_move])

    def lock(self):
        while os.path.exists(self.lock_file): # waits until the directory is free
            time.sleep(1)
            continue

        # locks the dir
        Path(self.lock_file).touch()

    def unlock(self):
        os.remove(self.lock_file)



