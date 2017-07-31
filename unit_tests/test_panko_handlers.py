# Copyright 2016 Canonical Ltd
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

from __future__ import absolute_import
from __future__ import print_function

import mock

import charms_openstack.test_utils as test_utils

import reactive.panko_handlers as handlers


class TestRegisteredHooks(test_utils.TestRegisteredHooks):

    def test_hooks(self):
        defaults = [
            'charm.installed',
            'shared-db.connected',
            'identity-service.connected',
            'identity-service.available',  # enables SSL support
            'config.changed',
            'update-status']
        hook_set = {
            'when': {
                'render_config': (
                    'shared-db.available',
                    'identity-service.available',
                ),
                'init_db': (
                    'config.rendered',
                ),
                'cluster_connected': (
                    'ha.connected',
                ),
                'provide_panko_url': (
                    'event-service.connected',
                    'config.rendered',
                ),
            },
            'when_not': {
                'disable_services': (
                    'config.rendered',
                ),
            },
        }
        # test that the hooks were registered via the
        # reactive.panko_handlers
        self.registered_hooks_test_helper(handlers, hook_set, defaults)


class TestHandlers(test_utils.PatchHelper):

    def setUp(self):
        super(TestHandlers, self).setUp()
        self.panko_charm = mock.MagicMock()
        self.patch_object(handlers.charm, 'provide_charm_instance',
                          new=mock.MagicMock())
        self.provide_charm_instance().__enter__.return_value = \
            self.panko_charm
        self.provide_charm_instance().__exit__.return_value = None

    def test_render_stuff(self):
        handlers.render_config('arg1', 'arg2')
        self.panko_charm.render_with_interfaces.assert_called_once_with(
            ('arg1', 'arg2')
        )
        self.panko_charm.assess_status.assert_called_once_with()
        self.panko_charm.enable_apache2_site.assert_called_once_with()

    def test_init_db(self):
        handlers.init_db()
        self.panko_charm.db_sync.assert_called_once_with()

    def test_provide_panko_url(self):
        mock_panko = mock.MagicMock()
        self.panko_charm.public_url = "http://panko:8777"
        handlers.provide_panko_url(mock_panko)
        mock_panko.set_panko_url.assert_called_once_with(
            "http://panko:8777"
        )

    def test_disable_services(self):
        handlers.disable_services()
        self.panko_charm.disable_services.assert_called_once_with()
