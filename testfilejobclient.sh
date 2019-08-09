#!/usr/bin/env bash

if [ "$#" -lt 1 ]; then
    echo "Please specify the basedir"
    exit
fi

for i in {1..20}; do
    echo "sleep 3 && echo \"hi $i\"" >> "$1/todo.txt"
done

# starts 5 clients
for i in {1..20}; do
    python3 filejobclient.py /tmp &
done

echo "Test finished"
