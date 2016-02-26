#!/usr/bin/python

import logging, os
from QXSConsolas.Cli import CliApp
from QXSConsolas.Command import SSH, call
from clint.textui import puts, colored, indent


class AppNotFoundException(Exception):
    pass

class SplunkDeployer:
    app = None

    def __init__(self):
        pass

    def _getAppDir(self, appname):
        try:
            appdir = (
                os.path.join(
                    self.app.configuration.get("Splunk.apps.default.directory") 
                ),
                appname
            )
            if not os.path.isdir(appdir):
                raise AppNotFoundException("The app \"" + app  + "\" does not exist.")
            return appdir
        except AppNotFoundException as e:
            raise e
        except:
            pass
        appdir = (
            os.path.join(
                self.app.configuration.get("Splunk.apps.default.directory") 
            ),
            appname
        )
        if not os.path.isdir(appdir):
            raise AppNotFoundException("The app \"" + app  + "\" does not exist.")
        return appdir

    def _deployApp(self, appname):
        self.app.logger.info("Deploying splunk app: " + appname)
        os.path.isdir(
            os.path.join(
                self.app.configuration.get("Splunk.apps.default.directory") 
            ),
            appname
        )
    def deploy(self, app):
        self.app = app
        if not "--env:" in self.app.options:
            self.app.options["--env:"] = "ALL"

        self.app.options["--env:"] = self.app.options["--env:"].upper()
        if not "--app:" in self.app.options:
            raise Exception("Please sepcify all required options")

        for appname in self.app.options['--app:']:
            self._deployApp(appname)
        """
        1. check is git folder? --> git pull
        2. pre commands
        3. check where to deploy? --> copy destination
        4. post commands
        print(call(["ssh", "localhost", ["echo", "hi"]], shell = True))
        print(call(["ssh", "localhost", ["echo", "hi"]], shell = False))
        s = SSH("localhost")
        print(s.call(["echo", "hi"]))
        """

    

@CliApp(
    Name = "Deploy an app",
    Description = "Deploys an app to a splunk environment",
    Opts = [ 
        { "argument": "--env:",   "default": "ALL", "description": "The targeted Splunk environment", "valuename": "ENV" },
        { "argument": "--app:",   "multiple": True,  "description": "The app that should be deployed", "valuename": "APP" },
    ]
)
def DeployApp(app):
    s = SplunkDeployer()
    s.deploy(app)

