# Overview

This charm provides the Panko event storage and API service for an OpenStack Cloud.

# Usage

Panko relies on services provided by keystone and a sqlalchemy-compatible database:

    juju deploy panko
    juju deploy keystone
    juju deploy percona-cluster
    juju add-relation panko percona-cluster
    juju add-relation panko keystone

# Bugs

Please report bugs on [Launchpad](https://bugs.launchpad.net/charm-panko/+filebug).

For general questions please refer to the OpenStack [Charm Guide](http://docs.openstack.org/developer/charm-guide/).
