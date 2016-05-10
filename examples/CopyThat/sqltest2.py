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


