#!/usr/bin/env python
#
from keystoneclient.v2_0 import Client as KeystoneClient
from cinderclient.v2.client import Client as CinderClient

import collectd

global NAME, OS_USERNAME, OS_PASSWORD, OS_TENANT_NAME, OS_AUTH_URL, OS_AUTH_STRATEGY, VERBOSE_LOGGING

NAME = "cinder_plugin"
OS_USERNAME = "username"
OS_PASSWORD = "password"
OS_TENANT_NAME = "tenantname"
OS_AUTH_URL = "http://localhost:5000/v2.0"
OS_AUTH_STRATEGY = "keystone"
VERBOSE_LOGGING = False

def get_stats(user, passwd, tenant, url, host=None):
    keystone = KeystoneClient(username=user, password=passwd, tenant_name=tenant, auth_url=url)

    # Find my uuid
    user_list = keystone.users.list()
    admin_uuid = ""
    for usr in user_list:
        if usr.name == user:
            admin_uuid = usr.id

    # Find out which tenants I have roles in
    tenant_list = keystone.tenants.list()
    my_tenants = list()
    for tenant in tenant_list:
        if keystone.users.list_roles(user=admin_uuid, tenant=tenant.id):
            my_tenants.append( { "name": tenant.name, "id": tenant.id } )

    prefix = "openstack.cinder"

    # Default data structure
    data = {}
    data["%s.total.images.count" % prefix] = 0
    data["%s.total.images.bytes" % prefix] = 0

    cinder_endpoint = keystone.service_catalog.url_for(service_type='volume')
    # for tenant in tenant_list:
    for tenant in my_tenants:
        client = CinderClient(cinder_endpoint, token=keystone.auth_token)

        tenant_name = tenant['name']

        data["%s.%s.volumes.count" % (prefix, tenant_name)] = 0
        data["%s.%s.volumes.bytes" % (prefix, tenant_name)] = 0

        volume_list = client.volumes.list()

        for volume in volume_list:
            data["%s.total.volumes.count" % prefix] += 1
            data["%s.total.volumes.bytes" % prefix] += int(volume['size'])
            data["%s.%s.volumes.count" % (prefix, tenant_name)] += 1
            data["%s.%s.volumes.bytes" % (prefix, tenant_name)] += int(volume['size'])

    return data

def configure_callback(conf):
    """Received configuration information"""
    global OS_USERNAME, OS_PASSWORD, OS_TENANT_NAME, OS_AUTH_URL
    for node in conf.children:
        if node.key == "Username":
            OS_USERNAME = node.values[0]
        elif node.key == "Password":
            OS_PASSWORD = node.values[0]
        elif node.key == "TenantName":
            OS_TENANT_NAME = node.values[0]
        elif node.key == "AuthURL":
            OS_AUTH_URL = node.values[0]
        elif node.key == "Verbose":
            VERBOSE_LOGGING = node.values[0]
        else:
            logger("warn", "Unknown config key: %s" % node.key)

def read_callback():
    logger("verb", "read_callback")

    info = get_stats(OS_USERNAME, OS_PASSWORD, OS_TENANT_NAME, OS_AUTH_URL)

    if not info:
        logger("err", "No information received")
        return

    for key in info.keys():
        logger('verb', 'Dispatching %s : %i' % (key, int(info[key])))
        val = collectd.Values(plugin=key)
        val.type = 'gauge'
        val.values = [int(info[key])]
        val.dispatch()

def logger(t, msg):
    if t == 'err':
        collectd.error('%s: %s' % (NAME, msg))
    if t == 'warn':
        collectd.warning('%s: %s' % (NAME, msg))
    elif t == 'verb' and VERBOSE_LOGGING == True:
        collectd.info('%s: %s' % (NAME, msg))

collectd.register_config(configure_callback)
collectd.warning("Initializing cinder plugin")
collectd.register_read(read_callback)
