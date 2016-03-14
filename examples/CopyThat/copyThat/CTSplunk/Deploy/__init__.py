import logging, os
from QXSConsolas.Cli import CliApp
from clint.textui import puts, colored, indent
from CTSplunk import NoRolesToDeployException, DeploymentException, AppNotFoundException
from SplunkDeployer import SplunkDeployer

@CliApp(
    Name = "Deploy an app",
    Description = "Deploys an app to a splunk environment",
    Opts = [ 
        { "argument": "--env:", "default": "ALL", "description": "The targeted Splunk environment", "valuename": "ENV" },
        { "argument": "--app:", "required": True, "multiple": True,  "description": "The app that should be deployed", "valuename": "APP" },
    ]
)
def DeployApp(app):
    s = SplunkDeployer()
    s.deploy(app)

