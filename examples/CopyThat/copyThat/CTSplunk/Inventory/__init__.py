import logging, os
from QXSConsolas.Cli import CliApp
from QXSConsolas.Configuration import GetSystemConfiguration
from CTSplunk import NoRolesToDeployException, DeploymentException, AppNotFoundException
from Inventory import IndexInventory
from sqlalchemy import create_engine

class NoInventoryEngine(Exception):
    pass

def GetInventoryEngine():
    if GetInventoryEngine._engine is None:
        raise NoInventoryEngine("SplunkInventory.datasource is invalid or not defined in the configuration.")
    return GetInventoryEngine._engine
# initialize the engine
try:
    GetInventoryEngine._engine = None
    GetInventoryEngine._engine = create_engine(GetSystemConfiguration().get("SplunkInventory.datasource"))
except:
    pass




@CliApp(
    Name = "Test Inventory",
    Description = "Tests the inventory",
    Opts = [ 
    ]
)
def Test(app):
    #transactions better
    with engine.begin() as conn:
        pass
