#!/usr/bin/python

import logging, os
from QXSConsolas.Configuration import Configuration
from QXSConsolas.Cli import CliApp
from QXSConsolas.Command import SSH, call
from clint.textui import puts, colored, indent
import timeit

class AppNotFoundException(Exception):
    pass

class SplunkDeployer:
    app = None

    def __init__(self):
        pass

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
        for role in envconfig:
            self.app.logger.info("Deploying to environment \"" + envname + "\" role \"" + role + "\"")
            for server in envconfig[role]["servers"]:
                srv = envconfig[role]["servers"][server]
                assert isinstance(srv, Configuration), "The role \"" + role + "\" in environment \"" + envname + "\" is not properly configured."
                for key in ["hostname", "path"]:
                    assert type(srv[key]) == str, "The role \"" + role + "\" in environment \"" + envname + "\" is not properly configured for key \"" + key + "\"."

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
        """
        1. check is git folder? --> git pull
        2. deploy to env
          2.2. for every type (idx, sh, fwd):
            2.2.1. pre commands
            2.2.2. check where to deploy? --> copy destination
            2.2.3. post commands
        print(call(["ssh", "localhost", ["echo", "hi"]], shell = True))
        print(call(["ssh", "localhost", ["echo", "hi"]], shell = False))
        s = SSH("localhost")
        print(s.call(["echo", "hi"]))
        """

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

