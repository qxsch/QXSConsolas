import logging, os
from QXSConsolas.Cli import CliApp
from clint.textui import puts, colored, indent
from CTSplunk import NoRolesToDeployException, DeploymentException, AppNotFoundException
from SplunkDeployer import SplunkDeployer

@CliApp(
    Name = "Deploy an app",
    Description = "Deploys an app to a splunk environment",
    Opts = [ 
        { "argument": "--app:", "required": True, "multiple": True,  "description": "The app that should be deployed", "valuename": "APP" },
        { "argument": "--env:", "default": "ALL", "description": "The targeted Splunk environment", "valuename": "ENV" },
    ]
)
def DeployApp(app):
    s = SplunkDeployer()
    s.deploy(app)

@CliApp(
    Name = "Create an app",
    Description = "Creates an app on a splunk environment",
    Opts = [ 
        { "argument": "--app:",  "required": True, "multiple": True,  "description": "The app that should be deployed", "valuename": "APP" },
        { "argument": "--role:", "required": True, "multiple": True,  "description": "Create the app on the following roles", "valuename": "ROLE" },
        { "argument": "--env:", "default": "ALL", "description": "The targeted Splunk environment", "valuename": "ENV" },
        { "argument": "-f", "description": "Force the app creation." },
    ]
)
def CreateApp(app):
    s = SplunkDeployer()
    s.create(app)

@CliApp(
    Name = "Remove an app",
    Description = "Removes an app from a splunk environment",
    Opts = [ 
        { "argument": "--app:",  "required": True, "multiple": True,  "description": "The app that should be deployed", "valuename": "APP" },
        { "argument": "--env:", "default": "ALL", "description": "The targeted Splunk environment", "valuename": "ENV" },
    ]
)
def RemoveApp(app):
    s = SplunkDeployer()
    s.remove(app)


