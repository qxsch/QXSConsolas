import logging, os
from QXSConsolas.Cli import CliApp
from QXSConsolas.Configuration import GetSystemConfiguration
from CTSplunk import NoRolesToDeployException, DeploymentException, AppNotFoundException
from Inventory import IndexInventory
from sqlalchemy import create_engine


def GetInventoryEngine():
    return GetInventoryEngine._engine
GetInventoryEngine._engine=create_engine(GetSystemConfiguration().get("SplunkInventory.datasource"))


@CliApp(
    Name = "Add Index to Inventory",
    Description = "Adds an index to the inventory",
    Opts = [ 
        #{ "argument": "--env:", "default": "ALL", "description": "The targeted Splunk environment", "valuename": "ENV" },
        #{ "argument": "--app:", "required": True, "multiple": True,  "description": "The app that should be deployed", "valuename": "APP" },
    ]
)
def AddIndex(app):
    with IndexInventory("/tmp/test.db") as inv:
       print(inv.list())

@CliApp(
    Name = "Test Inventory",
    Description = "Tests the inventory",
    Opts = [ 
    ]
)
def Test(app):
    print("hi")
    engine = create_engine("sqlite:///tmp/test.db")
    result = engine.execute(
        "select * from table where id=:emp_id",
        emp_id=3
    )
    result.close()

    # transactions
    #conn = engine.connet()
    #trans = conn.begin()
    #conn.execute("update talbe set spalte=:spalte where id=:emp_id", emp_id=3, spalte="hi")
    #trans.commit()
    #conn.close()


    #transactions better
    with engine.begin() as conn:
        conn.execute("update talbe set spalte=:spalte where id=:emp_id", emp_id=3, spalte="hi")
        # throw an exception to perform a rollback

