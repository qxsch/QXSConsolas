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

def GetConfiguredNodeEnvs(sep=", "):
    l = []
    envs = GetSystemConfiguration().get("SplunkNodes.envs")
    for env in envs:
        l.append(env)
    return str(sep).join(l)

def GetConfiguredNodeRoles(sep=", "):
    l = []
    envs = GetSystemConfiguration().get("SplunkNodes.envs")
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
        { "argument": "--app:",  "required": True, "multiple": True,  "description": "The app that should be created", "valuename": "APP" },
        { "argument": "--role:", "required": True, "multiple": True,  "description": "Create the app on the following roles.\nAvailable roles:\n * " + GetConfiguredRoles("\n * "), "valuename": "ROLE" },
        { "argument": "--env:",  "default": "ALL", "description": "The targeted Splunk environment.\nAvailable environments:\n * " + GetConfiguredEnvs("\n * "), "valuename": "ENV" },
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
        { "argument": "--app:", "required": True, "multiple": True,  "description": "The app that should be removed", "valuename": "APP" },
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


@CliApp(
    Name = "Backup an app",
    Description = "Backups an app from a splunk environment",
    Opts = [ 
        { "argument": "--app:",  "required": True, "multiple": True,  "description": "The app that should be backed up", "valuename": "APP" },
        { "argument": "--env:",  "required": True, "description": "The targeted Splunk environment.\nAvailable environments:\n * " + GetConfiguredNodeEnvs("\n * "), "valuename": "ENV" },
        { "argument": "--role:", "required": True, "description": "Take a backup from the following role.\nAvailable roles:\n * " + GetConfiguredNodeRoles("\n * "), "valuename": "ROLE" },
        { "argument": "--path:", "default": GetSystemConfiguration().get("SplunkDeployment.apps.default.directory"), "description": "The local path to store the backup.", "valuename": "PATH" },
    ]
)
def BackupApp(app):
    pass


@CliApp(
    Name = "Restore an app",
    Description = "Restores an app from a splunk environment",
    Opts = [ 
        { "argument": "--app:",  "required": True, "multiple": True,  "description": "The app that should be restored", "valuename": "APP" },
        { "argument": "--env:",  "required": True, "description": "The targeted Splunk environment.\nAvailable environments:\n * " + GetConfiguredNodeEnvs("\n * "), "valuename": "ENV" },
        { "argument": "--role:", "required": True, "description": "Restore a backup to the following role.\nAvailable roles:\n * " + GetConfiguredNodeRoles("\n * "), "valuename": "ROLE" },
        { "argument": "--path:", "default": GetSystemConfiguration().get("SplunkDeployment.apps.default.directory"), "description": "The local path to take the backup for the restore.", "valuename": "PATH" },
    ]
)
def RestoreApp(app):
    pass

@CliApp(
    Name = "Cross copy an app",
    Description = "Cross copies an app from a splunk environment to another",
    Opts = [ 
        { "argument": "--app:",  "required": True, "multiple": True,  "description": "The app that should be restored", "valuename": "APP" },
        { "argument": "--from-env:",  "required": True, "description": "The source Splunk environment.\nAvailable environments:\n * " + GetConfiguredNodeEnvs("\n * "), "valuename": "ENV" },
        { "argument": "--from-role:", "required": True, "description": "The source Splunk role.\nAvailable roles:\n * " + GetConfiguredNodeRoles("\n * "), "valuename": "ROLE" },
        { "argument": "--to-env:",  "required": True, "description": "The destination Splunk environment.\nAvailable environments:\n * " + GetConfiguredNodeEnvs("\n * "), "valuename": "ENV" },
        { "argument": "--to-role:", "required": True, "description": "The destination Splunk role.\nAvailable roles:\n * " + GetConfiguredNodeRoles("\n * "), "valuename": "ROLE" },
    ]
)
def CrossCopyApp(app):
    # create tmp dir
    #     backup to tmp dir
    #     restore from tmp dir
    # finally remove tmp dir
    pass

