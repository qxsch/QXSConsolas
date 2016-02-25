#!/usr/bin/python

import logging
from QXSConsolas.Cli import CliApp

@CliApp(
    Name = "Tests something",
    Description = "A very nice description cannot live without the text",
    Opts = [ 
        { "argument": "--name:",     "default": None, "multiple": True, "description": "den namen eingeben", "valuename": "NAME" },
        { "argument": "--verbose::", "default": 0,                      "description": "schwatzen?",         "valuename": "VERBOSITY" },
        { "argument": "-v::",        "default": 0,                      "references": "--verbose::",         "valuename": "VERBOSITY" },
        { "argument": "--name=",     "default": None,                   "description": "",                   "valuename": "NAME"}
    ]
)
def Test(app):
    print("Hallo Welt - Test")
    print("Options:")
    print(app.options)
    print("Arguments:")
    print(app.arguments)
    print("System Configuration:")
    print(app.configuration)
    if not app.data is None:
       print("Data:")
       print(app.data.dump())
    print("")
    s = ""
    for key in app.data:
        s = s + " " + str(app.data[key])
    print(s.strip())
    # injected logger
    app.logger.warning("hello from the injected loggger")
    # Using explicitely the root logger always logs to the console
    logging.debug("This is an info of the root logger")
    # Logging from myapp.lib
    myapp_cli_logger = logging.getLogger('myapp.cli')
    myapp_cli_logger.info("This is an info from myapp.cli")  # Not recorded
    myapp_cli_logger.warning("This is a warning from myapp.cli")  # -> sample.log
    myapp_cli_logger.error("This is an error from myapp.cli")  # -> sample.log
    myapp_cli_logger.critical("This is a critical from myapp.cli")  # -> sample.log
    print(1/0)
   
