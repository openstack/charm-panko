# Copyright 2017 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import collections
import subprocess

import charmhelpers.core.hookenv as hookenv
import charmhelpers.core.host as host

import charms_openstack.charm
import charms_openstack.adapters as adapters
import charms_openstack.ip as os_ip


PANKO_DIR = '/etc/panko'
PANKO_CONF = os.path.join(PANKO_DIR, 'panko.conf')
PANKO_APACHE_SITE = 'panko-api'
PANKO_WSGI_CONF = '/etc/apache2/sites-available/{}.conf'.format(
    PANKO_APACHE_SITE)


charms_openstack.charm.use_defaults('charm.default-select-release')


class PankoCharmRelationAdapters(adapters.OpenStackAPIRelationAdapters):
    relation_adapters = {
        'shared_db': adapters.DatabaseRelationAdapter,
        'cluster': adapters.PeerHARelationAdapter,
    }


class PankoCharm(charms_openstack.charm.HAOpenStackCharm):

    """
    Charm for Juju deployment of Panko
    """

    # Internal name of charm
    service_name = name = 'panko'

    # First release supported
    release = 'ocata'

    # List of packages to install for this charm
    packages = ['panko-api', 'python-apt', 'python-keystonemiddleware',
                'apache2', 'libapache2-mod-wsgi']

    api_ports = {
        'panko-api': {
            os_ip.PUBLIC: 8777,
            os_ip.ADMIN: 8777,
            os_ip.INTERNAL: 8777,
        }
    }

    default_service = 'panko-api'

    service_type = 'panko'

    services = ['apache2']

    required_relations = ['shared-db', 'identity-service']

    restart_map = {
        PANKO_CONF: services,
        PANKO_WSGI_CONF: ['apache2'],
    }

    ha_resources = ['vips', 'haproxy']

    release_pkg = 'panko-common'

    package_codenames = {
        'panko-common': collections.OrderedDict([
            ('2', 'mitaka'),
            ('3', 'newton'),
            ('4', 'ocata'),
            ('5', 'pike'),
            ('6', 'queens'),
            ('7', 'rocky'),
        ]),
    }

    sync_cmd = ['panko-dbsync',
                '--log-file=/var/log/panko/panko-upgrade.log']

    adapters_class = PankoCharmRelationAdapters

    def install(self):
        super(PankoCharm, self).install()
        # NOTE(jamespage): always pause panko-api service as we force
        #                  execution with Apache2+mod_wsgi
        host.service_pause('panko-api')

    def enable_apache2_site(self):
        """Enable Panko API apache2 site if rendered or installed"""
        if os.path.exists(PANKO_WSGI_CONF):
            check_enabled = subprocess.call(
                ['a2query', '-s', PANKO_APACHE_SITE]
            )
            if check_enabled != 0:
                subprocess.check_call(['a2ensite',
                                       PANKO_APACHE_SITE])
                host.service_reload('apache2',
                                    restart_on_failure=True)

    def get_database_setup(self):
        return [{
            'database': 'panko',
            'username': 'panko',
            'hostname': hookenv.unit_private_ip()}, ]

    def disable_services(self):
        '''Disable all services related to panko'''
        for svc in self.services:
            host.service_pause(svc)

    def enable_services(self):
        '''Enable all services related to panko'''
        for svc in self.services:
            host.service_resume(svc)
