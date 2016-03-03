#!/usr/bin/python

import sys, os, logging

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
	".".join(os.path.basename(__file__).split(".")[0:-1])
    )
)
import QXSConsolas


try:
  QXSConsolas.run()
except Exception as e:
   logging.exception(e)

