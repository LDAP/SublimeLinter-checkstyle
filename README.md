SublimeLinter-checkstyle
================================

[![Build Status](https://travis-ci.org/SublimeLinter/SublimeLinter-contrib-checkstyle.svg?branch=master)](https://travis-ci.org/SublimeLinter/SublimeLinter-contrib-checkstyle)

This linter plugin for [SublimeLinter](https://github.com/SublimeLinter/SublimeLinter) provides an interface to [checkstyle](__linter_homepage__). It will be used with files that have the “java” syntax.

## Installation
SublimeLinter must be installed in order to use this plugin. 

Please use [Package Control](https://packagecontrol.io) to install the linter plugin.

Before installing this plugin, you must ensure that `java` is installed on your system.

In order for `java` to be executed by SublimeLinter, you must ensure that its path is available to SublimeLinter. The docs cover [troubleshooting PATH configuration](http://sublimelinter.readthedocs.io/en/latest/troubleshooting.html#finding-a-linter-executable).

## Settings
- SublimeLinter settings: http://sublimelinter.readthedocs.org/en/latest/settings.html
- Linter settings: http://sublimelinter.readthedocs.org/en/latest/linter_settings.html

Additional SublimeLinter-checkstyle settings:

|Setting|Description    |
|:------|:--------------|
|version|`latest` or a specific version from https://github.com/checkstyle/checkstyle/releases/|
|config |/path/to/checkstyle/config.xml|
|debug  |`True` or `False`|
