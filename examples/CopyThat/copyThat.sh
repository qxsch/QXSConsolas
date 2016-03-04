#!/bin/bash

find "$(dirname "$0")/" -name '*.pyc' -type f -delete 

rm "$(dirname "$0")/sample.log"

"${0/.sh/.py}" "$@"

echo "------ sample log ------"
cat "$(dirname "$0")/sample.log"
