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
#   This plugin collects OpenStack glance information, including number
#   of images and bytes used per tenant.
#
# collectd:
#   http://collectd.org
# OpenStack Glance:
#   http://docs.openstack.org/developer/glance/
# collectd-python:
#   http://collectd.org/documentation/manpages/collectd-python.5.shtml
#
from glanceclient.v2.client import Client as GlanceClient

import collectd
import traceback

import base

class GlancePlugin(base.Base):

    def __init__(self):
        base.Base.__init__(self)
        self.prefix = 'openstack-glance'

    def get_stats(self):
        """Retrieves stats from glance"""
        keystone = self.get_keystone()

        data = { self.prefix: {} }
        glance_endpoint = keystone.service_catalog.url_for(service_type='image')

        tenant_list = keystone.tenants.list()
        client = GlanceClient(glance_endpoint, token=keystone.auth_token)
        for tenant in tenant_list:
            data[self.prefix]["tenant-%s" % tenant.name] = { 'images': {} }
            data_tenant = data[self.prefix]["tenant-%s" % tenant.name]
            data_tenant['images']['count'] = 0
            data_tenant['images']['bytes'] = 0

            image_list = client.images.list(tenant_id=tenant.name)
            for image in image_list:
                data_tenant['images']['count'] += 1
                data_tenant['images']['bytes'] += int(image['size'])

        return data

try:
    plugin = GlancePlugin()
except Exception as exc:
    collectd.error("openstack-glance: failed to initialize glance plugin :: %s :: %s"
            % (exc, traceback.format_exc()))

def configure_callback(conf):
    """Received configuration information"""
    plugin.config_callback(conf)

def read_callback():
    """Callback triggerred by collectd on read"""
    plugin.read_callback()

collectd.register_config(configure_callback)
collectd.register_read(read_callback, plugin.interval)
