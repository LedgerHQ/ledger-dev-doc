# Ledger Developer Documentation

This repository contains the core documentation for developers who wish to make
BOLOS applications, and for those who would like to gain a better understanding
of the features offered by BOLOS and the background theory behind our products.

The latest version of this repository can be viewed, pre-built, here:
https://ledger.readthedocs.io.

## Contributing

If you notice a mistake or would like to contribute, feel free to issue a pull
request or talk to us on the [developer Slack](https://ledger-dev.slack.com).

If you make a contribution with a pull request, don't bother bumping the version
number yourself. We will do this at some point if your pull request is accepted.

## Building

If you wish, you may install Sphinx and build this documentation into a
collection of HTML files yourself.

Firstly, make sure you have [pip3
installed](https://linuxize.com/post/how-to-install-pip-on-ubuntu-18.04/).

Secondly, install Sphinx and the Read the Docs theme:

```
pip3 install sphinx sphinx_rtd_theme
```

Finally, build:

```
make html
```

You will need internet access for intersphinx to work properly.
