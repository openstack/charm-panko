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

import charms_openstack.charm as charm
import charms.reactive as reactive

import charm.openstack.panko as panko  # noqa


charm.use_defaults(
    'charm.installed',
    'shared-db.connected',
    'identity-service.connected',
    'identity-service.available',  # enables SSL support
    'config.changed',
    'update-status')


@reactive.when_not('config.rendered')
def disable_services():
    with charm.provide_charm_instance() as charm_class:
        charm_class.disable_services()


@reactive.when('shared-db.available')
@reactive.when('identity-service.available')
def render_config(*args):
    """Render the configuration for charm when all the interfaces are
    available.
    """
    with charm.provide_charm_instance() as charm_class:
        charm_class.render_with_interfaces(args)
        charm_class.enable_apache2_site()
        charm_class.enable_services()
        charm_class.assess_status()
    reactive.set_state('config.rendered')


# db_sync checks if sync has been done so rerunning is a noop
@reactive.when('config.rendered')
def init_db():
    with charm.provide_charm_instance() as charm_class:
        charm_class.db_sync()


@reactive.when('ha.connected')
def cluster_connected(hacluster):
    """Configure HA resources in corosync"""
    with charm.provide_charm_instance() as charm_class:
        charm_class.configure_ha_resources(hacluster)
        charm_class.assess_status()


@reactive.when('event-service.connected')
@reactive.when('config.rendered')
def provide_panko_url(event_service):
    with charm.provide_charm_instance() as charm_class:
        event_service.set_panko_url(charm_class.public_url)
