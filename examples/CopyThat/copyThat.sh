#!/bin/bash

# check deletes
# find "$(dirname "$0")/copyThat/CopyThat" -name '*.pyc' -type f

rm -f "$(dirname "$0")/sample.log"
rm -f "$(dirname "$0")/splunksample.log"
find "$(dirname "$0")/copyThat/CopyThat" -name '*.pyc' -type f -delete 

cd "$(dirname "$0")"


echo
echo "----- running copyThat.py -----"

./copyThat.py "$@"

echo
echo "------ log file ---------------"
cat "$(dirname "$0")/sample.log"
echo
echo "------ splunk log file --------"
cat "$(dirname "$0")/splunksample.log"

