Workflow management tool (WMT)
==============================

WMT provides a GUI to enable users to design workflows and perform analysis and optimization.

Links
-----

*   ASAP Project [Official Page](http://www.asap-fp7.eu/)

Setup
-----
For demostration reasons a Linux operating system like Ubuntu it is assumed in this step. In Windows or other Linux distributions the equivalents should be done.

The project uses [nginx](http://nginx.org/), [php-fpm](http://php-fpm.org/) and [python](https://www.python.org/). To install these packages execute the command:
`sudo apt-get nginx php-fpm python`

The project's root directory stores a configuration file for nginx: `wmt.conf.default`.
It should be changed appropriately: on line 5 `set $ROOT "/your/path/to/wmt";`.
Then you can use this file for nginx server configuration:
`ln -s ~/your/path/to/wmt/wmt.conf /your/nginx/installation/servers/`

To build the project use [Grunt](http://gruntjs.com/). Installation of Grunt's command line interface (CLI) globally can be done with the following commands:

1.  `sudo apt-get npm`
2.  `sudo npm install -g grunt-cli`

The project is configured with a `package.json` and a `Gruntfile.js`, it's very easy to start working with Grunt:

1.  Go to the project's root directory.
2.  Install project dependencies with `npm install`.
3.  Run Grunt with `grunt`.

Usage of a tool
---------------

### Workflow Design

Creating a workflow from scratch can be done by following steps:

1.  First, click new workflow on the top of the page.
2.  Then, create a graph of a workflow: add nodes and datastores using buttons add datastore and add node;
    connect them using button add links, when it is pressed сlicking on the first then the second nodes adds an edge between them.
3.  Add tasks into the nodes: choose a node;
    click add task on the left sidebar;
    choose from the list of operators and then edit metadata to your needs.
4.  Save the workflow, click save workflow on the top navbar.


