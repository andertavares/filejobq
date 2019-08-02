# File Job Queue

A simple file-based job queue.

You just need to create a file named `todo.txt` in a directory of your choice (let's call it `dir`) and put the list of jobs to execute, one per line. Each job is simply a command to run.

Then, to start a file job client, just type `./filejobclient.py dir`. You can start as many clients as your machine allows. As a client starts a job, it moves the job from `todo.txt` to `doing.txt`. When the client finishes the job, it moves the job from `doing.txt` to `done.txt` and looks for a new job in `todo.txt`, repeating this process until there are no more jobs in `todo.txt`. 

The clients halt after 10 unsucessfull attempts to start a job (i.e. `todo.txt` is empty), each attempt is done after 5 seconds. 

## Requirements

Python 3 (tested in 3.6.8)
