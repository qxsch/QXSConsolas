#!/usr/bin/python

import sys, os, logging

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "copyThat"
    )
)

from sqlalchemy import create_engine
from CTSplunk.Inventory.GenericInventory import GenericInventory, IndexInventory
from clint.textui import puts, columns
from clint.textui import puts, columns, colored


engine = create_engine('sqlite:////tmp/db.sqlite')
with engine.begin() as trans:
    ii = IndexInventory(trans)
    #print(ii.getAttributes())
    print("List all:")
    print(ii.search())
    print("IndexName='test' search:")
    print(ii.search(indexName="test"))
    print("IndexName='test%' search:")
    print(ii.search(indexName="test%"))
    print("IndexName='test%' and SourceType='*' search:")
    print(ii.search(indexName="test%", sourcetypeName="*"))
    print("IndexOwner='MW' and RetentionDays=20 search:")
    print(ii.lookupAttributes(ii.search(IndexOwner='MW', RetentionDays=20)))

    width = 0
    attrs = ii.getAttributes()
    for k in attrs:
        width = max(width, len(attrs[k]["attr_name"]))
    width = width + 1
    if width > 40:
        width = 40

    for entry in ii.lookupAttributes(ii.list()):
        puts(columns(["ID:", width], [colored.green(str(entry["object_id"])), None]))
        puts(columns(["Index:", width], [colored.green(str(entry["indexName"])), None]))
        puts(columns(["Sourcetype:", width], [colored.green(str(entry["sourcetypeName"])), None]))
        for k, v in entry["attributes"].iteritems():
            puts(columns([attrs[k]["attr_name"]+":", width], [str(v), None]))
        puts()



