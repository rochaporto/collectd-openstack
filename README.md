collectd-openstack
==================

## Overview

A set of collectd plugins monitoring and publishing metrics for OpenStack components.

It includes plugins to monitor the different components, including:

* Glance
* Keystone
* Nova
* Swift

The original code was taken from the [rackspace chef cookbook](https://github.com/rochaporto/openstack-monitoring), and adapted as needed.

## Requirements

It assumes an existing installation of [collectd](http://collectd.org/documentation.shtml).

Check its documentation for details.

## Setup and Configuration

The example configuration(s) below assume the plugins to be located under `/usr/lib/collectd/plugins`,
if you install using the deb package that's where they end up too.

Each plugin should have its own config file, under `/etc/collectd/conf.d/<pluginname>.conf`, which
should follow some similar to:
```
# cat /etc/collectd/conf.d/keystone.conf

<LoadPlugin "python">
    Globals true
</LoadPlugin>

<Plugin "python">
    ModulePath "/usr/lib/collectd/plugins"

    Import "keystone_plugin"

    <Module "keystone_plugin">
        Verbose false
                AuthURL "https://api.example.com:5000/v2.0"
                Username "admin"
                Password "123456"
                TenantName "openstack"
                Verbose "False"
    </Module>
</Plugin>
```

### Puppet

If you use puppet for configuration, then try this excelent [collectd](https://github.com/pdxcat/puppet-module-collectd) module.

It has plenty of docs on how to use it, but for our specific plugins:
```
  collectd::plugin::python { 'keystone':
    modulepath => '/usr/lib/collectd/plugins',
    module     => 'keystone_plugin',
    config     => {
      'Username'   => 'admin',
      'Password'   => '123456',
      'TenantName' => 'openstack',
      'AuthURL'    => 'https://api1.example.com:5000/v2.0',
      'Verbose'    => 'true',
    },
  }
```

## Limitations

The debian packaging files are provided, but don't expect the deb in the official repos.

## Development

Most of the code was taken from other sources, and adapted as needed.

All contributions more than welcome, just send pull requests.

## License

GPLv2 (check LICENSE).

## Contributors

Ricardo Rocha <ricardo@catalyst.net.nz>

## Support

Please log tickets and issues at the [github home](https://github.com/rochaporto/collectd-openstack/issues).

## Additional Notes

### Building the debian package

```
tar -zcvf ../collectd-openstack_1.20140502.orig.tar.gz *
dpkg-buildpackage -us -uc
```
