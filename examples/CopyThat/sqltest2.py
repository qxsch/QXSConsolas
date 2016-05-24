#!/usr/bin/python

import sys, os, logging

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "copyThat"
    )
)
from QXSConsolas.Configuration import GetSystemConfiguration, InitSystemConfiguration
InitSystemConfiguration(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "copyThat/config.yaml"
    )
)

from CTSplunk.Inventory import GetInventoryEngine
from CTSplunk.Inventory.Inventory import GenericInventory, IndexInventory
from CTSplunk.Inventory.Handler import ConsoleHandler
from clint.textui import puts, columns, colored, prompt, validators


engine = GetInventoryEngine()
with engine.begin() as trans:
    ii = IndexInventory(trans)
    #print(ii.getAttributes())
    #print("List all:")
    #print(ii.search())
    #print("IndexName='test' search:")
    #print(ii.search(indexName="test"))
    #print("IndexName='test%' search:")
    #print(ii.search(indexName="test%"))
    #print("IndexName='test%' and SourceType='*' search:")
    #print(ii.search(indexName="test%", sourcetypeName="*"))
    #print("IndexOwner='MW' and RetentionDays=20 search:")
    #print(ii.lookupAttributes(ii.search(IndexOwner='MW', RetentionDays=20)))

    h = ConsoleHandler(None, ii)
    h.display(ii.list())
   
    print("INSERTING XYZ") 
    print(ii.create('xyz', 'xyz', IndexOwner="MW", RetentionDays="20", CostCenter="X", DailyQuotaGB="2"))
    h.display(ii.search(indexName="xyz", sourcetypeName="xyz"))
    print("")

    print("UPDATING COSTCENTER AND TARGETEDUSERS") 
    print(ii.updateAttributes(None, 'xyz', 'xyz', CostCenter="ABC", TargetedUsers="ALL"))
    h.display(ii.search(indexName="xyz", sourcetypeName="xyz"))
    print("")

    print("REMOVING TARGETEDUSERS") 
    print(ii.removeAttributes(None, 'xyz', 'xyz', [ "TargetedUsers" ]))
    h.display(ii.search(indexName="xyz", sourcetypeName="xyz"))
    print("")

    print("DELETING XYZ") 
    print(ii.delete(None, 'xyz', 'xyz'))
    h.display(ii.search(indexName="xyz", sourcetypeName="xyz"))
    print("")
    #print(h.askForRequiredAttributes())
    #print(h.askForAllAttributes())

    #print(ii.delete('xyz', 'xyz'))
    raise RuntimeError("Rollback")


# http://docs.sqlalchemy.org/en/latest/core/selectable.html#sqlalchemy.sql.expression.TableClause.update
# http://docs.sqlalchemy.org/en/latest/core/tutorial.html#inserts-updates-and-deletes

"""
# Standard non-empty input
name = prompt.query("What's your name?")

# Set validators to an empty list for an optional input
language = prompt.query("Your favorite tool (optional)?", validators=[])

# Shows a list of options to select from
inst_options = [{'selector':'1','prompt':'Full','return':'full'},
                {'selector':'2','prompt':'Partial','return':'partial'},
                {'selector':'3','prompt':'None','return':'no install'}]
inst = prompt.options("Full or Partial Install", inst_options)

# Use a default value and a validator
path = prompt.query('Installation Path', default='/usr/local/bin/', validators=[validators.PathValidator()])

puts(colored.blue('Hi {0}. Install {1} {2} to {3}'.format(name, inst, language or 'nothing', path)))
"""

