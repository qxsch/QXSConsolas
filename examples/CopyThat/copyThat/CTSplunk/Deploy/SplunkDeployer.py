#!/usr/bin/python

import logging, os, os.path
from QXSConsolas.Configuration import Configuration
from QXSConsolas.Cli import CliApp
from QXSConsolas.Command import SSH, call, replaceVars
from clint.textui import puts, colored, indent
from DeployRoles import getSplunkRoles
import timeit
from CTSplunk import NoRolesToDeployException, DeploymentException, AppNotFoundException


class SplunkDeployer:
    app = None
    _affectedServers = {}
    _roles = {
        "SHD": None,
        "IDX": None,
        "UFM": None
    }

    def __init__(self):
        self._roles = getSplunkRoles()

    def _getAppDirConfig(self, appname):
        try:
            appconfig = self.app.configuration.get("SplunkDeployment.apps")[appname]
            appdir = appconfig.get("directory")
            if not os.path.isdir(appdir):
                raise AppNotFoundException("The app \"" + appname  + "\" does not exist in \"" + appdir + "\".")
            return [appdir, appconfig] 
        except AppNotFoundException as e:
            raise e
        except:
            pass
        appconfig = self.app.configuration.get("SplunkDeployment.apps.default")
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
    
    def _deployAppToEnv(self, ssh, appname, appdir, appconfig, envname, envconfig):
        # configuration check
        for role in envconfig:
            assert "role" in envconfig[role], "The key \"SplunkDeployment.envs.'" + envname + "'.'" + role + "'.role\" is missing"
            assert envconfig[role]["role"] in self._roles, "The key \"SplunkDeployment.envs.'" + envname + "'.'" + role + "'.role\" is not properly configured. Found \"" + envconfig[role]["role"] + "\", but expecting one of: " + ", ".join(self._roles.keys())
            for server in envconfig[role]["servers"]:
                srv = envconfig[role]["servers"][server]
                assert isinstance(srv, Configuration), "The role \"" + role + "\" in environment \"" + envname + "\" is not properly configured."
                for key in ["hostname", "path"]:
                    assert key in srv, "The key \"SplunkDeployment.envs.'" + envname + "'.'" + role + "'.'" + server +  "'.'" + key + "'\" is missing"
                    assert type(srv[key]) == str and srv[key] != "", "The key \"SplunkDeployment.envs.'" + envname + "'.'" + role + "'.'" + server +  "'.'" + key + "'\" is not properly configured"
        # check where to deploy && run optional pre local
        deployToRoles = []
        for role in envconfig:
            for server in envconfig[role]["servers"]:
                srv = envconfig[role]["servers"][server]
                ssh.host = srv["hostname"]
                remoteappdir = os.path.join(srv["path"], appname)
                rc, stdout, stderr = ssh.call([ "test", "-d", os.path.join(srv["path"], appname) ])
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
                    ssh.host = srv["hostname"]
                    remoteappdir = os.path.join(srv["path"], appname)
                    if not self._runRoleCommand(envconfig[role], "preremote", ssh, remoteappdir):
                        self.app.logger.debug("Won't deploy to role \"" + role + "\" in environment \"" + envname + "\", because of a failed preremote command on server \"" + srv["hostname"] + "\"")
                        deployToRoles.remove(role)
                        break;
        if not deployToRoles:
            raise NoRolesToDeployException("Cannot deploy the app \"" + appname + "\" to any roles for environment \"" + envname + "\"")
        # deploy app to servers 
        for role in deployToRoles:
            self.app.logger.info("Deploying to environment \"" + envname + "\" role \"" + role + "\" (" + envconfig[role]["role"] + ")")
            self._runBeforeDeployment(ssh, envname, role)
            self._roles[envconfig[role]["role"]].setRoleInfo(self.app, envname, envconfig, role, envconfig[role])
            for server in envconfig[role]["servers"]:
                srv = envconfig[role]["servers"][server]
                ssh.host = srv["hostname"]
                remoteappdir = os.path.join(srv["path"], appname)
                self.app.logger.debug("Deploying app to server: " + srv["hostname"] + ":" + srv["path"])
                self._roles[envconfig[role]["role"]].deployAppToServer(ssh, appname, appdir, appconfig, remoteappdir, srv)
        # run optional post local && post remote commands
        for role in deployToRoles:
            self._runRoleCommand(envconfig[role], "postlocal", None, appdir)
            for server in envconfig[role]["servers"]:
                srv = envconfig[role]["servers"][server]
                ssh.host = srv["hostname"]
                remoteappdir = os.path.join(srv["path"], appname)
                self._runRoleCommand(envconfig[role], "postremote", ssh, remoteappdir)

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

    def _deployApp(self, ssh, appname):
        self.app.logger.info("Deploying splunk app: " + appname)
        appdir, appconfig = self._getAppDirConfig(appname)
        self.app.logger.debug("App found in path: " + appdir)
        # 1. git folder? -> git pull
        self._handleGitDir(appname, appdir, appconfig)
        # 2. deploy to envs
        envs = self.app.configuration.get("SplunkDeployment.envs")
        if self.app.options["--env:"] == "ALL":
            for env in envs:
                self._deployAppToEnv(ssh, appname, appdir, appconfig, env, envs[env])
        else:
            env = self.app.options["--env:"]
            if env in envs:
                self._deployAppToEnv(ssh, appname, appdir, appconfig, env, envs[env])
            else:
                raise RuntimeError("The environment \"" + env + "\" does not exist.")

    def _runBeforeDeployment(self, ssh, envname, rolename):
        if not envname in self._affectedServers:
            self._affectedServers[envname] = {}
        if not rolename in self._affectedServers[envname]:
            self._affectedServers[envname][rolename] = True
            envs = self.app.configuration.get("SplunkDeployment.envs")
            self._roles[envs[envname][rolename]["role"]].setRoleInfo(self.app, envname, envs[envname], rolename, envs[envname][rolename])
            for server in envs[envname][rolename]["servers"]:
                srv = envs[envname][rolename]["servers"][server]
                ssh.host = srv["hostname"]
                self.app.logger.debug("Running before deployment task on server: " + srv["hostname"])
                self._roles[envs[envname][rolename]["role"]].doBeforeDeployment(ssh, srv)

    def _runAfterDeployment(self, ssh):
        envs = self.app.configuration.get("SplunkDeployment.envs")
        for envname in self._affectedServers:
            for rolename in self._affectedServers[envname]:
                self._roles[envs[envname][rolename]["role"]].setRoleInfo(self.app, envname, envs[envname], rolename, envs[envname][rolename])
                for server in envs[envname][rolename]["servers"]:
                    srv = envs[envname][rolename]["servers"][server]
                    ssh.host = srv["hostname"]
                    self.app.logger.debug("Running after deployment task on server: " + srv["hostname"])
                    self._roles[envs[envname][rolename]["role"]].doAfterDeployment(ssh, srv)

    def deploy(self, app):
        self._affectedServers = {}
        self.app = app
        if not "--env:" in self.app.options:
            self.app.options["--env:"] = "ALL"
        else:
            self.app.options["--env:"] = self.app.options["--env:"].upper()

        t = timeit.default_timer()

        ssh = SSH()
        if "ALL"  in self.app.options['--app:']:
            self.app.logger.warning("Deploying ALL splunk apps")
            apps = self.app.configuration.get("SplunkDeployment.apps")
            defaultdir = self.app.configuration.get("SplunkDeployment.apps.default.directory")
            # default apps
            for d in [d for d in os.listdir(defaultdir) if os.path.isdir(os.path.join(defaultdir, d))]:
                if d in apps:
                    continue
                try:
                    self._deployApp(ssh, d)
                except Exception as e:
                    self.app.logger.exception(e)
            # other apps
            for d in apps:
                if d == "default":
                    continue
                try:
                    apps[d].get("directory")
                except:
                    continue
                try:
                    self._deployApp(ssh, d)
                except Exception as e:
                    self.app.logger.exception(e)
        else:
            for appname in self.app.options['--app:']:
                self._deployApp(ssh, appname)

        self._runAfterDeployment(ssh)

        t = timeit.default_timer() - t
        if t < 10:
            self.app.logger.info("Deployment took: {:.4f} seconds".format(t))
        else:
            self.app.logger.warning("Deployment took: {:.4f} seconds".format(t))
            

