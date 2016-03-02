#!/bin/bash

find "$(dirname "$0")/" -name '*.pyc' -type f -delete 

cd "$(dirname "$0")"

"${0/.sh/.py}" "$@"


