#!/bin/bash

find "$(dirname "$0")/" -name '*.pyc' -type f -delete 


"${0/.sh/.py}" "$@"

