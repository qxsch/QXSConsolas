#!/usr/bin/python

import logging
from QXSConsolas.Cli import CliApp
from QXSConsolas.Command import SSH, call


@CliApp(
    Name = "Deploy an app",
    Description = "Deploys an app to a splunk environment",
    Opts = [ 
        { "argument": "--env:",   "default": "ALL", "description": "The targeted Splunk environment", "valuename": "ENV" },
        { "argument": "--app:",   "multiple": True,  "description": "The app that should be deployed", "valuename": "APP" },
    ]
)
def DeployApp(app):
    if not "--env:" in app.options:
        app.options["--env:"] = "ALL"
    app.options["--env:"] = app.options["--env:"].upper()
    if not "--app:" in app.options:
        raise Exception("Please sepcify all required options")

    print(app.options)
    print("Deploying to " + str(app.options["--env:"]))
    """
    1. check is git folder? --> git pull
    2. pre commands
    3. check where to deploy? --> copy destination
    4. post commands
    """
    print(call(["ssh", "localhost", ["echo", "hi"]], shell = True))
    print(call(["ssh", "localhost", ["echo", "hi"]], shell = False))
    s = SSH("localhost")
    print(s.call(["echo", "hi"]))
