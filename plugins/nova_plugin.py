#!/usr/bin/env python
#
# vim: tabstop=4 shiftwidth=4

# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; only version 2 of the License is applicable.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# Authors:
#   Ricardo Rocha <ricardo@catalyst.net.nz>
#
# About this plugin:
#   This plugin collects OpenStack nova information, including limits and
#   quotas per tenant.
#
# collectd:
#   http://collectd.org
# OpenStack Nova:
#   http://docs.openstack.org/developer/nova
# collectd-python:
#   http://collectd.org/documentation/manpages/collectd-python.5.shtml
#
from novaclient.client import Client as NovaClient
from novaclient import exceptions

import collectd
import traceback

import base

class NovaPlugin(base.Base):

    def __init__(self):
        base.Base.__init__(self)
        self.prefix = 'openstack-nova'

    def get_stats(self):
        """Retrieves stats from nova"""
        keystone = self.get_keystone()

        tenant_list = keystone.tenants.list()

        data = { self.prefix: {} }
        for tenant in tenant_list:
            client = NovaClient('2', self.username, self.password, self.tenant, self.auth_url)

            data[self.prefix][tenant.name] = { 'limits': {}, 'quotas': {} }
            data_tenant = data[self.prefix][tenant.name]

            # Get absolute limits for tenant
            limits = client.limits.get(tenant_id=tenant.id).absolute
            for limit in limits:
                data_tenant['limits'][limit.name] = limit.value

            # Quotas for tenant
            quotas = client.quotas.get(tenant.name)
            for item in ('cores', 'fixed_ips', 'floating_ips', 'instances',
                'key_pairs', 'ram', 'security_groups'):
                data_tenant['quotas'][item] = getattr(quotas, item)

        return data

try:
    plugin = NovaPlugin()
except Exception as exc:
    collectd.error("openstack-nova: failed to initialize nova plugin :: %s :: %s"
            % (exc, traceback.format_exc()))
    
def configure_callback(conf):
    """Received configuration information"""
    plugin.config_callback(conf)

def read_callback():
    """Callback triggerred by collectd on read"""
    plugin.read_callback()

collectd.register_config(configure_callback)
collectd.register_read(read_callback)
