collectd-openstack
==================

## Overview

A set of collectd plugins monitoring and publishing metrics for OpenStack components.

## Screenshots

![image](https://raw.github.com/rochaporto/collectd-openstack/master/public/openstack-usage.png)

## Plugins and Metrics

There are several plugins, mapping to each of the openstack components.

Find below a list of the available plugins and the metrics they publish.

* cinder_plugin
  * openstack-cinder.&lt;tenant>.volumes.count (number of tenant volumes)
  * openstack-cinder.&lt;tenant>.volumes.bytes (total bytes of tenant volumes)
  * openstack-cinder.&lt;tenant>.volume-snapshots.count (number of tenant snapshots)
  * openstack-cinder.&lt;tenant>.volume-snapshots.bytes (total bytes of tenant snapshots)
  * openstack-cinder.&lt;tenant>.limites-{maxTotalVolumeGigabytes,maxTotalVolumes}
* glance_plugin
  * openstack-glance.&lt;tenant>.images.count (number of tenant images)
  * openstack-glance.&lt;tenant>.images.bytes (total bytes of tenant images)
* keystone_plugin
  * openstack-keystone.&lt;tenant>.users.count (number of tenant users)
  * openstack-keystone.totals.tenants.count (total number of tenants)
  * openstack-keystone.totals.users.count (total number of users)
  * openstack-keystone.totals.services.count (total number of services)
  * openstack-keystone.totals.endpoints.count (total number of endpoints)
* neutron_plugin
  * openstack-neutron.&lt;tenant>.networks.count (number of tenant networks)
  * openstack-neutron.&lt;tenant>.subnets.count (number of tenant subnets)
  * openstack-neutron.&lt;tenant>.routers.count (number of tenant routers)
  * openstack-neutron.&lt;tenant>.ports.count (number of tenant ports)
  * openstack-neutron.&lt;tenant>.floatingips.count (number of tenant floating ips)
  * openstack-neutron.&lt;tenant>.quotas-{floatingip,ikepolicy,ipsec_site_connection,ipsecpolicy,network,
                                          port,router,security_group,security_group_rule,subnet}
* nova_plugin
  * openstack-nova.&lt;tenant>.limits.{maxImageMeta,maxPersonality,maxPersonalitySize,maxSecurityGroupRules,
                                       maxSecurityGroups,maxServerMeta,maxTotalCores,maxTotalFloatingIps,
                                       maxTotalInstances,maxTotalKeypairs,maxTotalRAMSize}
    (limits on each metric, per tenant)
  * openstack-nova.&lt;tenant>.quotas.{cores,fixed_ips,floating_ips,instances,key_pairs,,ram,security_groups}
    (quotas on each metric, per tenant)
  * openstack-nova.cluster.gauge.config-AllocationRatioCores (overcommit ratio for vcpus)
  * openstack-nova.cluster.gauge.config-AllocationRatioRamMB (overcommit ratio for ram - in MB)
  * openstack-nova.cluster.gauge.config-ReservedCores (reserved vcpus on the whole cluster)
  * openstack-nova.cluster.gauge.config-ReservedRamMB (reserved ram on the whole cluster - in MB)
  * openstack-nova.cluster.gauge.config-ReservedNodeCores (reserved cores per node)
  * openstack-nova.cluster.gauge.config-ReservedNodeRamMB (reserved ram per node - in MB)
  * openstack-nova.&lt;hypervisor-hostname>.{current_workload,free_disk_gb,free_ram_mb,hypervisor_version,
                                             memory_mb,memory_mb_overcommit,memory_mb_overcommit_withreserve,
                                             memory_mb_used,running_vms,vcpus,vcpus_overcommit,
                                             vcpus_overcommit_withreserve,vcpus_used}

## Requirements

It assumes an existing installation of [collectd](http://collectd.org/documentation.shtml).

Check its documentation for details.

## Setup and Configuration

The example configuration(s) below assume the plugins to be located under `/usr/lib/collectd/plugins`.

If you're under ubuntu, consider installing from [this ppa](https://launchpad.net/~rocha-porto/+archive/collectd).

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
        Username "admin"
        Password "123456"
        TenantName "openstack"
        AuthURL "https://api.example.com:5000/v2.0"
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

All contributions more than welcome, just send pull requests.

## License

GPLv2 (check LICENSE).

## Contributors

Ricardo Rocha <ricardo@catalyst.net.nz>

## Support

Please log tickets and issues at the [github home](https://github.com/rochaporto/collectd-openstack/issues).

## Additional Notes

### Ubuntu Packaging

[These instructions](http://packaging.ubuntu.com/html/packaging-new-software.html) should give full details.

In summary, do this once to prepare your environment:
```
pbuilder-dist precise create
```

and for every release (from master):
```
mkdir /tmp/build-collectd-os
cd /tmp/build-collectd-os
wget https://github.com/rochaporto/collectd-openstack/archive/master.zip
unzip master.zip
tar zcvf collectd-openstack-0.2.tar.gz collectd-openstack-master/
bzr dh-make collectd-openstack 0.2 collectd-openstack-0.2.tar.gz
cd collectd-openstack
bzr builddeb -S
cd ../build-area
pbuilder-dist precise build collectd-openstack_0.2-1ubuntu1.dsc
dput ppa:rocha-porto/collectd ../collectd-openstack_0.2-1ubuntu1_source.changes
```
