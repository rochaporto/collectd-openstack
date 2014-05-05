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
#   Helper object for all plugins.
#
# collectd:
#   http://collectd.org
# collectd-python:
#   http://collectd.org/documentation/manpages/collectd-python.5.shtml
#
import collectd

class Helper(object):

    def __init__(self):
        self.username = 'admin'
        self.password = '123456'
        self.tenant = 'openstack'
        self.auth_url = 'http://api.example.com:5000/v2.0'
        self.verbose = True
        self.prefix = ''

    def config(self, conf, prefix=None):
        """Takes a collectd conf object and fills in the local config."""
        self.prefix = prefix
        for node in conf.children:
            if node.key == "Username":
                self.username = node.values[0]
            elif node.key == "Password":
                self.password = node.values[0]
            elif node.key == "TenantName":
                self.tenant = node.values[0]
            elif node.key == "AuthURL":
                self.auth_url = node.values[0]
            elif node.key == "Verbose":
                self.verbose = node.values[0]
            elif node.key == "Prefix":
                self.prefix = node.values[0]
            else:
                collectd.warning("%s: unknown config key: %s" % (self.prefix, node.key))

    def dispatch(self, stats):
        """
        Dispatches the given stats.
        
        stats should be something like:

        {'plugin': {'plugin_instance': {'type': {'type_instance': <value>, ...}}}}
        """
        if not stats:
            collectd.error("%s: failed to retrieve stats from glance" % self.prefix)
            return

        self.logverbose("dispatching %d new stats :: %s" % (len(stats), stats))
        try:
            for plugin in stats.keys():
                for plugin_instance in stats[plugin].keys():
                    for type in stats[plugin][plugin_instance].keys():
                        for type_instance in stats[plugin][plugin_instance][type].keys():
                            self.dispatch_value(plugin, plugin_instance, 
                                    type, type_instance,
                                    stats[plugin][plugin_instance][type][type_instance])
        except Exception as exc:
            collectd.error("%s: failed to dispatch values :: %s" % (self.prefix, exc))

    def dispatch_value(self, plugin, plugin_instance, type, type_instance, value):
        """Looks for the given stat in stats, and dispatches it"""
        self.logverbose("dispatching value %s.%s.%s.%s=%s" 
                % (plugin, plugin_instance, type, type_instance, value))
    
        val = collectd.Values(type='gauge')
        val.plugin=plugin
        val.plugin_instance=plugin_instance
        val.type_instance="%s-%s" % (type, type_instance)
        val.values=[value]
        val.dispatch()

    def logverbose(self, msg):
        collectd.info("%s: %s" % (self.prefix, msg))

