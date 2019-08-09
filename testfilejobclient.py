import os
import sys
import filejobclient

if __name__ == '__main__':
    basedir = sys.argv[1]

    # creates a todo.txt file
    with open(os.path.join(basedir, 'todo.txt'), 'w') as todo:
        for i in range(6):
            todo.write("sleep 3 && hi %d\n" % i)

    # starts 5 clients
    for i in range(6):
        client = filejobclient.Client('/tmp')
        client.run()

    print('Test finished')
