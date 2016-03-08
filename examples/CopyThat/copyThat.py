#!/usr/bin/python

import sys, os, logging

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        ".".join(os.path.basename(__file__).split(".")[0:-1])
    )
)
import QXSConsolas
from QXSConsolas.Configuration import GetSystemConfiguration, InitSystemConfiguration


try:
    InitSystemConfiguration(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            ".".join(os.path.basename(__file__).split(".")[0:-1]),
            "config.yaml"
        )
    )
    rc = QXSConsolas.run()
    logging.shutdown()
    sys.exit(rc)
except Exception as e:
    logging.exception(e)
    logging.shutdown()
    sys.exit(10)
