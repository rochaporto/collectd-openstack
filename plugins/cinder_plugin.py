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
#   This plugin collects OpenStack cinder information, including stats on
#   volumes and snapshots usage per tenant.
#
# TODO: Start using cinder v2 api
#
# collectd:
#   http://collectd.org
# OpenStack Cinder:
#   http://docs.openstack.org/developer/cinder
# collectd-python:
#   http://collectd.org/documentation/manpages/collectd-python.5.shtml
#
#!/usr/bin/env python
#
from cinderclient.client import Client as CinderClient

import collectd
import traceback

import base

class CinderPlugin(base.Base):

    def __init__(self):
        base.Base.__init__(self)
        self.prefix = 'openstack-cinder'

    def get_stats(self):
        """Retrieves stats from cinder"""
        keystone = self.get_keystone()

        tenant_list = keystone.tenants.list()

        tenants = {}
        data = { self.prefix: {} }

        client = CinderClient('1', self.username, self.password, self.tenant, self.auth_url)
        # Get count and bytes for volumes
        for tenant in tenant_list:
            data[self.prefix]["tenant-%s" % tenant.name] = {
                'volumes': { 'count': 0, 'bytes': 0 },
                'volume-snapshots': { 'count': 0, 'bytes': 0 }
            }
            data_tenant = data[self.prefix]["tenant-%s" % tenant.name]

            # volumes for tenant
            volumes = client.volumes.list(search_opts={'tenant_id': tenant.id})
            for volume in volumes:
                data_tenant['volumes']['count'] += 1
                data_tenant['volumes']['bytes'] += (volume.size * 1024 * 1024 * 1024)

            # snapshots for tenant
            volume_snapshots = client.volume_snapshots.list(search_opts={'tenant_id': tenant.id})
            for snapshot in volume_snapshots:
                data_tenant['volume-snapshots']['count'] += 1
                data_tenant['volume-snapshots']['bytes'] += (snapshot.size * 1024 * 1024 * 1024)

        return data

try:
    plugin = CinderPlugin()
except Exception as exc:
    collectd.error("openstack-cinder: failed to initialize cinder plugin :: %s :: %s"
            % (exc, traceback.format_exc()))

def configure_callback(conf):
    """Received configuration information"""
    plugin.config_callback(conf)

def read_callback():
    """Callback triggerred by collectd on read"""
    plugin.read_callback()

collectd.register_config(configure_callback)
collectd.register_read(read_callback, plugin.interval)
