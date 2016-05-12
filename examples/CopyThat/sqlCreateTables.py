#!/usr/bin/python

import sys, os, logging

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "copyThat"
    )
)

from sqlalchemy import create_engine
from CTSplunk.Inventory.Metadata import CreateAllInventoryTables

os.remove('/tmp/db.sqlite')
engine = create_engine('sqlite:////tmp/db.sqlite')

CreateAllInventoryTables(engine)

