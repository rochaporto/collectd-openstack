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
#   This plugin collects OpenStack network information.
#
# collectd:
#   http://collectd.org
# OpenStack Neutron:
#   http://docs.openstack.org/developer/neutron/
# collectd-python:
#   http://collectd.org/documentation/manpages/collectd-python.5.shtml
#
#
from neutronclient.neutron.client import Client as NeutronClient

import collectd
import traceback

import base

class NeutronPlugin(base.Base):

    def __init__(self):
        base.Base.__init__(self)
        self.prefix = 'openstack-neutron'

    def get_stats(self):
        """Retrieves stats from neutron"""
        keystone = self.get_keystone()

        data = { self.prefix: {} }

        tenants = {}
        tenant_list = keystone.tenants.list()
        for tenant in tenant_list:
            tenants[tenant.id] = tenant.name
            data[self.prefix][tenant.name] = {
                'networks': { 'count': 0 },
                'subnets': { 'count': 0 },
                'routers': { 'max': 0 },
                'ports': { 'max': 0 },
                'floatingips': { 'max': 0 },
            }

        neutron_endpoint = keystone.service_catalog.url_for(service_type='network')

        client = NeutronClient('2.0', endpoint_url=neutron_endpoint, token=keystone.auth_token)

        # Get network count
        network_list = client.list_networks()['networks']
        for network in network_list:
            try:
                tenant = tenants[network['tenant_id']]
            except KeyError:
                continue
            data[self.prefix][tenant]['networks']['count'] += 1
            for subnet in network['subnets']:
                data[self.prefix][tenant]['subnets']['count'] += 1

        # Get network quotas
        for tenant in tenant_list:
            quotas = client.list_quotas(tenant_id=tenant.id)['quotas']
            if len(quotas) > 0:
                quota = quotas[0]
                data[self.prefix][tenant.name]['networks']['max'] = quota['network']
                data[self.prefix][tenant.name]['subnets']['max'] = quota['subnet']
                data[self.prefix][tenant.name]['routers']['max'] = quota['router']
                data[self.prefix][tenant.name]['ports']['max'] = quota['port']
                data[self.prefix][tenant.name]['floatingips']['max'] = quota['floatingip']

        return data

try:
    plugin = NeutronPlugin()
except Exception as exc:
    collectd.error("openstack-neutron: failed to initialize neutron plugin :: %s :: %s"
            % (exc, traceback.format_exc()))

def configure_callback(conf):
    """Received configuration information"""
    plugin.config_callback(conf)

def read_callback():
    """Callback triggerred by collectd on read"""
    plugin.read_callback()

collectd.register_config(configure_callback)
collectd.register_read(read_callback)
