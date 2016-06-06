import logging, os
from QXSConsolas.Cli import CliApp
from clint.textui import puts, colored, indent
from CTSplunk import NoRolesToDeployException, DeploymentException, AppNotFoundException
from SplunkDeployer import SplunkDeployer
from QXSConsolas.Configuration import GetSystemConfiguration


def GetConfiguredEnvs(sep=", "):
    l = [ "ALL" ]
    envs = GetSystemConfiguration().get("SplunkDeployment.envs")
    for env in envs:
        l.append(env)
    return str(sep).join(l)

def GetConfiguredRoles(sep=", "):
    l = []
    envs = GetSystemConfiguration().get("SplunkDeployment.envs")
    for env in envs:
        for role in envs[env]:
            if role not in l:
                l.append(role)
    return str(sep).join(l)




@CliApp(
    Name = "Deploy an app",
    Description = "Deploys an app to a splunk environment",
    Opts = [ 
        { "argument": "--app:", "required": True, "multiple": True,  "description": "The app that should be deployed", "valuename": "APP" },
        { "argument": "--env:", "default": "ALL", "description": "The targeted Splunk environment.\nAvailable environments:\n * " + GetConfiguredEnvs("\n * "), "valuename": "ENV" },
    ]
)
def DeployApp(app):
    s = SplunkDeployer()
    try:
        s.WarnDeploymentTime = float(app.data["WarnDeploymentTime"])
    except ValueError:
        app.logger.debug("Failed to set the WarnDeploymentTime")
    except:
        pass
    s.deploy(app)

@CliApp(
    Name = "Create an app",
    Description = "Creates an app on a splunk environment",
    Opts = [ 
        { "argument": "--app:",  "required": True, "multiple": True,  "description": "The app that should be deployed", "valuename": "APP" },
        { "argument": "--role:", "required": True, "multiple": True,  "description": "Create the app on the following roles.\nAvailable roles:\n * " + GetConfiguredRoles("\n * "), "valuename": "ROLE" },
        { "argument": "--env:", "default": "ALL", "description": "The targeted Splunk environment.\nAvailable environments:\n * " + GetConfiguredEnvs("\n * "), "valuename": "ENV" },
        { "argument": "-f", "description": "Force the app creation." },
    ]
)
def CreateApp(app):
    s = SplunkDeployer()
    try:
        s.WarnDeploymentTime = float(app.data["WarnDeploymentTime"])
    except ValueError:
        app.logger.debug("Failed to set the WarnDeploymentTime")
    except:
        pass
    s.create(app)

@CliApp(
    Name = "Remove an app",
    Description = "Removes an app from a splunk environment",
    Opts = [ 
        { "argument": "--app:",  "required": True, "multiple": True,  "description": "The app that should be deployed", "valuename": "APP" },
        { "argument": "--env:", "default": "ALL", "description": "The targeted Splunk environment.\nAvailable environments:\n * " + GetConfiguredEnvs("\n * "), "valuename": "ENV" },
    ]
)
def RemoveApp(app):
    s = SplunkDeployer()
    try:
        s.WarnDeploymentTime = float(app.data["WarnDeploymentTime"])
    except ValueError:
        app.logger.debug("Failed to set the WarnDeploymentTime")
    except:
        pass
    s.remove(app)


