#! usr/bin/bash

set -e 

GITIGNORE_PATH=".gitignore"

while IFS= read -r line; 
do
    rm -rf $line
done < $GITIGNORE_PATH
