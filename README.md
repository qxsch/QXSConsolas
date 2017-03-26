[![Project Status](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active)

# QXSConsolas
A Python console application framework with clint, cli route configuration and logging configuration

### A Full example

See our CopyThat example to manage Splunk roles: https://github.com/qxsch/QXSConsolas/tree/master/examples/CopyThat

### A simple example

```python

import logging, os
from QXSConsolas.Cli import CliApp
from clint.textui import puts, colored, indent

@CliApp(
    Name = "Deploy an app",
    Description = "Deploys an app to a splunk environment",
    Opts = [ 
        { "argument": "--env:", "default": "ALL", "description": "The targeted Splunk environment", "valuename": "ENV" },
        { "argument": "--app:", "required": True, "multiple": True,  "description": "The app that should be deployed", "valuename": "APP" },
    ]
)
def DeployApp(app):
    puts("Deploying your apps")
    with indent(4):
        for appname in app.options["--app:"]:
            puts("Deploying " + appname)
            # some code here
            successful = True
            if successful:
                app.logger.info("App " + appname + " has been deployed")
            else:
                app.logger.error("App " + appname + " couldn't be deployed")

```
