# Ansible for NSX-T POLICY API

# Overview

This project is an unofficial project because NSX-T editor (Vmware) currently don't provide ansible modules to interact with new nsx-t api policy.

This repository contains NSX-T Ansible Modules, which one can use with
Ansible to work with [VMware NSX-T Data Center][vmware-nsxt].

[vmware-nsxt]: https://www.vmware.com/products/nsx.html

For general information about Ansible, visit the [GitHub project page][an-github].

[an-github]: https://github.com/ansible/ansible

These modules are maintained by [Forterro](https://www.forterro.com/).

Documentation on the NSX platform can be found at the [NSX-T Documentation page](https://docs.vmware.com/en/VMware-NSX-T/index.html)

### Supported NSX Objects/Workflows
The modules in this repository are focused on enabling automation of installation workflows of NSX-T with new API formely called policy.

### Branch Information

> To be updated when first release will be available

#### Deployment and installation modules

##### Logical networking modules
* nsxt_policy_edgeclusters_facts
* nsxt_policy_edges_facts
* nsxt_policy_inventory_groups
* nsxt_policy_inventory_groups_facts
* nsxt_policy_ipblock_facts
* nsxt_policy_ipblocks
* nsxt_policy_ippools
* nsxt_policy_ippools_facts
* nsxt_policy_ippools_static_subnets
* nsxt_policy_ippools_static_subnets_facts
* nsxt_policy_lb_monitor_profiles_facts
* nsxt_policy_lb_pools
* nsxt_policy_lb_pools_facts
* nsxt_policy_lb_tcp_monitor_profiles
* nsxt_policy_lb_virtual_servers
* nsxt_policy_lb_virtual_servers_facts
* nsxt_policy_load_balancers
* nsxt_policy_load_balancers_facts
* nsxt_policy_router_locale_services
* nsxt_policy_router_locale_services_facts
* nsxt_policy_router_locale_services_interfaces
* nsxt_policy_router_static_routes
* nsxt_policy_router_static_routes_facts
* nsxt_policy_security_policies
* nsxt_policy_security_policies_facts
* nsxt_policy_segments
* nsxt_policy_segments_facts
* nsxt_policy_segments_ports
* nsxt_policy_segments_ports_facts
* nsxt_policy_segments_security_profiles
* nsxt_policy_segments_security_profiles_facts
* nsxt_policy_tier0s
* nsxt_policy_tier0s_facts
* nsxt_policy_tier1s
* nsxt_policy_tier1s_facts
* nsxt_policy_transport_zones_facts
* nsxt_policy_virtual_machines_tags

# Prerequisites
We assume that ansible is already installed.
These modules support ansible version 2.7 and onwards.

* PyVmOmi - Python library for vCenter api.

* OVF Tools - Ovftool is used for ovf deployment.


# Build & Run

Install PyVmOmi
```
pip install --upgrade pyvmomi pyvim requests ssl
```
Download and Install Ovf tool 4.3 - [Ovftool](https://my.vmware.com/web/vmware/details?downloadGroup=OVFTOOL430&productId=742)
(Note: Using ovftool version 4.0/4.1 causes OVA/OVF deployment failure with Error: cURL error: SSL connect error\nCompleted with errors\n)

Clone [ansible-for-nsxt-policy](https://github.com/forterro/ansible-for-nsxt-policy).

> To be updated when first release will be available

# Interoperability

The following versions of NSX are supported:

 * NSX-T 2.5
 * Ansible 2.9

# Contributing

The forterro/ansible-for-nsxt-policy project team welcomes contributions from the community.

Because this project is based on  [ansible-for-nsxt](https://github.com/vmware/ansible-for-nsxt) we keep rules from vmware github

Before you start working with ansible-for-nsxt-policy, please read our [Developer Certificate of Origin](https://cla.vmware.com/dco). All contributions to this repository must be signed as described on that page. Your signature certifies that you wrote the patch or have the right to pass it on as an open-source patch. For more detailed information, refer to [CONTRIBUTING.md](CONTRIBUTING.md).

# Support

The NSX-T Ansible modules in this repository are community supported. For bugs and feature requests please open a Github Issue and label it appropriately. As this is a community supported solution there is no SLA for resolutions.

# License

[GPLv3](https://www.gnu.org/licenses/gpl-3.0.fr.html)
