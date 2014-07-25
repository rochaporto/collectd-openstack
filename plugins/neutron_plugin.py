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
            data[self.prefix]["tenant-%s" % tenant.name] = {
                    'quotas': {},
                    'networks': { 'count': 0, },
                    'subnets': { 'count': 0,  },
                    'routers': { 'count': 0,  },
                    'ports': { 'count': 0,  },
                    'floatingips': { 'count': 0, },
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
            data[self.prefix]["tenant-%s" % tenant]['networks']['count'] += 1
            for subnet in network['subnets']:
                data[self.prefix]["tenant-%s" % tenant]['subnets']['count'] += 1

        # Get floating ips
        floatingip_list = client.list_floatingips()['floatingips']
        for floatingip in floatingip_list:
            try:
                tenant = tenants[floatingip['tenant_id']]
            except KeyError:
                continue
            data[self.prefix]["tenant-%s" % tenant]['floatingips']['count'] += 1

        # Get network quotas
        quotas = client.list_quotas()['quotas']
        for quota in quotas:
            try:
                data_tenant = data[self.prefix]["tenant-%s" % tenants[quota['tenant_id']]]
            except KeyError:
                continue
            for item in ('floatingip', 'ikepolicy', 'ipsec_site_connection',
                  'ipsecpolicy', 'network', 'port', 'router',
                  'security_group', 'security_group_rule', 'subnet'):
                data_tenant['quotas'][item] = quota[item]

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
collectd.register_read(read_callback, plugin.interval)
