#!/usr/bin/python

import logging, os
from QXSConsolas.Configuration import Configuration
from QXSConsolas.Cli import CliApp
from QXSConsolas.Command import SSH, call, replaceVars
from clint.textui import puts, colored, indent
from DeployRoles import getSplunkRoles
import timeit


class NoRolesToDeployException(Exception):
    pass
class DeploymentException(Exception):
    pass
class AppNotFoundException(Exception):
    pass

class SplunkDeployer:
    app = None
    _roles = {
        "SHD": None,
        "IDX": None,
        "UFM": None
    }

    def __init__(self):
        self._roles = getSplunkRoles()

    def _getAppDirConfig(self, appname):
        try:
            appconfig = self.app.configuration.get("Splunk.apps")[appname]
            appdir = appconfig.get("directory")
            if not os.path.isdir(appdir):
                raise AppNotFoundException("The app \"" + appname  + "\" does not exist in \"" + appdir + "\".")
            return [appdir, appconfig] 
        except AppNotFoundException as e:
            raise e
        except:
            pass
        appconfig = self.app.configuration.get("Splunk.apps.default")
        appdir = os.path.join(
            appconfig.get("directory"),
            appname
        )

        if not os.path.isdir(appdir):
            raise AppNotFoundException("The app \"" + appname  + "\" does not exist in \"" + appdir + "\".")
        return [appdir, appconfig]

    def _handleGitDir(self, appname, appdir, appconfig):
        rc, stdout, stderr = call(["git", "rev-parse", "--is-inside-work-tree"], cwd=appdir, shell = False)
        if not (rc == 0 and stdout.strip().lower() == "true"):
            self.app.logger.debug("App is not a git repository")
            return None

        self.app.logger.info("Running git pull ")

        rc, stdout, stderr = call(["git", "pull"], cwd=appdir, shell = False)
        if rc != 0:
            raise RuntimeError("Failed to run git pull with error: " + (stdout.strip() + "\n" + stderr.strip()).strip())

        return None
    
    def _deployAppToEnv(self, appname, appdir, appconfig, envname, envconfig):
        s = SSH()
        # configuration check
        for role in envconfig:
            assert "role" in envconfig[role], "The key \"Splunk.envs.'" + envname + "'.'" + role + "'.role\" is missing"
            assert envconfig[role]["role"] in self._roles, "The key \"Splunk.envs.'" + envname + "'.'" + role + "'.role\" is not properly configured. Found \"" + envconfig[role]["role"] + "\", but expecting one of: " + ", ".join(self._roles.keys())
            for server in envconfig[role]["servers"]:
                srv = envconfig[role]["servers"][server]
                assert isinstance(srv, Configuration), "The role \"" + role + "\" in environment \"" + envname + "\" is not properly configured."
                for key in ["hostname", "path"]:
                    assert key in srv, "The key \"Splunk.envs.'" + envname + "'.'" + role + "'.'" + server +  "'.'" + key + "'\" is missing"
                    assert type(srv[key]) == str and srv[key] != "", "The key \"Splunk.envs.'" + envname + "'.'" + role + "'.'" + server +  "'.'" + key + "'\" is not properly configured"
        # check where to deploy && run optional pre local
        deployToRoles = []
        for role in envconfig:
            for server in envconfig[role]["servers"]:
                srv = envconfig[role]["servers"][server]
                s.host = srv["hostname"]
                remoteappdir = os.path.join(srv["path"], appname)
                rc, stdout, stderr = s.call([ "test", "-d", os.path.join(srv["path"], appname) ])
                if rc != 0:
                    self.app.logger.debug("Won't deploy to role \"" + role + "\" in environment \"" + envname + "\", because the app does not exist on server \"" + srv["hostname"] + "\"")
                    continue
                deployToRoles.append(role)
        # run optional pre local && pre remote commands
        for role in deployToRoles:
            if not self._runRoleCommand(envconfig[role], "prelocal", None, appdir):
                self.app.logger.debug("Won't deploy to role \"" + role + "\" in environment \"" + envname + "\", because of a failed prelocal command")
                deployToRoles.remove(role)
            else:
                for server in envconfig[role]["servers"]:
                    srv = envconfig[role]["servers"][server]
                    s.host = srv["hostname"]
                    remoteappdir = os.path.join(srv["path"], appname)
                    if not self._runRoleCommand(envconfig[role], "preremote", s, remoteappdir):
                        self.app.logger.debug("Won't deploy to role \"" + role + "\" in environment \"" + envname + "\", because of a failed preremote command on server \"" + srv["hostname"] + "\"")
                        deployToRoles.remove(role)
                        break;
        if not deployToRoles:
            raise NoRolesToDeployException("Cannot deploy the app \"" + appname + "\" to any roles for environment \"" + envname + "\"")
        # deploy app to servers 
        for role in deployToRoles:
            self.app.logger.info("Deploying to environment \"" + envname + "\" role \"" + role + "\" (" + envconfig[role]["role"] + ")")
            self._roles[envconfig[role]["role"]].setRoleInfo(self.app, appname, appdir, appconfig, envname, envconfig, role, envconfig[role])
            for server in envconfig[role]["servers"]:
                srv = envconfig[role]["servers"][server]
                s.host = srv["hostname"]
                remoteappdir = os.path.join(srv["path"], appname)
                self.app.logger.debug("Deploying app to server: " + srv["hostname"] + ":" + srv["path"])
                self._roles[envconfig[role]["role"]].deployAppToServer(s, remoteappdir, srv)
        # run optional post local && post remote commands
        for role in deployToRoles:
            self._runRoleCommand(envconfig[role], "postlocal", None, appdir)
            for server in envconfig[role]["servers"]:
                srv = envconfig[role]["servers"][server]
                s.host = srv["hostname"]
                remoteappdir = os.path.join(srv["path"], appname)
                self._runRoleCommand(envconfig[role], "postremote", s, remoteappdir)

    def _runRoleCommand(self, roleconfig, key, ssh, appdir):
        if not(key in roleconfig and isinstance(roleconfig[key], Configuration)):
            return True # wrong configuration, nothign done successfully
        for cmdkey in roleconfig[key]:
            if isinstance(roleconfig[key][cmdkey].configuration, list):
                cmd = replaceVars(
                    roleconfig[key][cmdkey].configuration,
                    {
                        "trigger": key,
                        "appdir": appdir
                    }
                )
                if ssh is None:
                    rc, stdout, stderr = call(cmd, shell=True)
                    if rc != 0:
                        self.app.logger.warning(key.upper()  + " Command " + str(cmd) + " failed with rc " + rc + ":\n" + (stdout.strip() + "\n" + stderr.strip()).strip())
                        return False
                    else:
                        self.app.logger.debug(key.upper() + " Command " + str(cmd) + " was successful:\n" + (stdout.strip() + "\n" + stderr.strip()).strip())
                else:
                    rc, stdout, stderr = ssh.call(cmd)
                    if rc != 0:
                        self.app.logger.warning(key.upper()  + " Command " + str(cmd) + " failed on host \"" + ssh.host + "\" with rc " + rc + ":\n" + (stdout.strip() + "\n" + stderr.strip()).strip())
                        return False
                    else:
                        self.app.logger.debug(key.upper() + " Command " + str(cmd) + " was successful on host \"" + ssh.host + "\":\n" + (stdout.strip() + "\n" + stderr.strip()).strip())
        return True

    def _deployApp(self, appname):
        self.app.logger.info("Deploying splunk app: " + appname)
        appdir, appconfig = self._getAppDirConfig(appname)
        self.app.logger.debug("App found in path: " + appdir)
        # 1. git folder? -> git pull
        self._handleGitDir(appname, appdir, appconfig)
        # 2. deploy to envs
        envs = self.app.configuration.get("Splunk.envs")
        if self.app.options["--env:"] == "ALL":
            for env in envs:
                self._deployAppToEnv(appname, appdir, appconfig, env, envs[env])
        else:
            env = self.app.options["--env:"]
            if env in envs:
                self._deployAppToEnv(appname, appdir, appconfig, env, envs[env])
            else:
                raise RuntimeError("The environment \"" + env + "\" does not exist.")

    def deploy(self, app):
        self.app = app
        if not "--env:" in self.app.options:
            self.app.options["--env:"] = "ALL"
        else:
            self.app.options["--env:"] = self.app.options["--env:"].upper()

        t = timeit.default_timer()

        for appname in self.app.options['--app:']:
            self._deployApp(appname)

        t = timeit.default_timer() - t
        if t < 10:
            self.app.logger.info("Deployment took: {:.4f} seconds".format(t))
        else:
            self.app.logger.warning("Deployment took: {:.4f} seconds".format(t))
            

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

