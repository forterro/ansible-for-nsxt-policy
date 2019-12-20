#!/usr/bin/python
#
# Copyright (c) 2019 Forterro
# Copyright 2018 VMware, Inc.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import absolute_import, division, print_function

__metaclass__ = type


ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: nsxt_policy_tier0s_locale_services

short_description: Manage a tier0 locale service with policy APIS
description:

version_added: "2.9"

author: Olivier Gintrand

options:
  hostname:
    description: Deployed NSX manager hostname.
    required: true
    type: str
  username:
    description: The username to authenticate with the NSX manager.
    required: true
    type: str
  password:
    description: The password to authenticate with the NSX manager.
    required: true
    type: str
  validate_certs:
    description: Insecure connection to NSX manager.
    required: false
    default: true
    type: boolean
  port:
    description: NSX manager api port
    required: false
    default: 443
    type: int
  state:
    choices:
    - present
    - absent
    description:  "State can be either 'present' or 'absent'.
                  'present' is used to create or update resource.
                  'absent' is used to delete resource."
    required: true
    type: str
  display_name:
    description:  Identifier to use when displaying entity in logs or GUI
                  Maximum length: 255
    required: false
    type: str
    default: default
  description:
    description: Description
    required: false
    type: str
  tier0:
    description: Identifier for concerned tier0 (display_name)
    required: true
    type: str
  edge_cluster_path:
    description: Policy path to edge cluster.
    required: true
    type: str
  ha_vip_configs:
    description:  This configuration can be defined only for Active-Standby Tier0 gateway to provide redundancy.
                  For mulitple external interfaces, multiple HA VIP configs must be defined and each config will
                  pair exactly two external interfaces. The VIP will move and will always be owned by the Active
                  node. When this property is configured, configuration of dynamic-routing is not allowed.
                  - external_interface_paths:
                      description:  Policy paths to Tier0 external interfaces for providing redundancy
                                    Policy paths to Tier0 external interfaces which are to be paired to provide
                                    redundancy. Floating IP will be owned by one of these interfaces depending
                                    upon which edge node is Active.
                                    Minimum items: 2
                      required: true
                      type: list
                    vip_subnets:
                      description:  Array of IP address subnets which will be used as floating IP addresses.
                                    Minimum items: 1
                                    Maximum items: 2
                      required: true
                      type: list
                      - ip_addresses
                          description: IP addresses assigned to interface
                          required: true
                          type: list
                        prefix_len:
                          description: Subnet prefix length
                          required: true
                          type: int
                    enabled:
                      description: Flag to enable this HA VIP config.
                      required: false
                      default: true
                      type: bool
    required: false
    type: list
  preferred_edge_paths:
    description:  Edge node path
                  Policy paths to edge nodes. Specified edge is used as preferred edge
                  cluster member when failover mode is set to PREEMPTIVE, not
                  applicable otherwise.
                  Maximum items: 2
    required: false
    type: list



"""

EXAMPLES = """

nsxt_policy_tier0s_locale_services:
  hostname: "nsxvip.domain.local"
  username: "admin"
  password: "Vmware1!"
  validate_certs: false
  display_name: "My_first_tier0s_locale_services"
  description: "My first tier0s_locale_services automated created by Ansible for NSX-T policy"
  tier0: "my_tier0"
  edge_cluster_path: "/infra/sites/default/enforcement-points/default/edge-clusters/b0181f39-24e6-455c-a1d8-7c65e9abe7ae",
  preferred_edge_paths: "/infra/sites/default/enforcement-points/default/edge-clusters/b0181f39-24e6-455c-a1d8-7c65e9abe7ae/edge-nodes/b2236f0f-295f-47f8-a37c-f42139083c49"

"""


RETURN = """# """

from ansible.module_utils.vmware_nsxt_policy_apis import (
    vmware_argument_spec,
    nsx_module_execution,
)
from ansible.module_utils.basic import AnsibleModule


def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(
        display_name=dict(required=False, type="str", default="default"),
        description=dict(required=False, type="str"),
        state=dict(required=True, choices=["present", "absent"]),
        tier0=dict(required=True, type="str"),
        edge_cluster_path=dict(required=True, type="str"),
        ha_vip_configs=dict(required=False, type="list"),
        preferred_edge_paths=dict(required=False, type="list"),
        route_redistribution_types=dict(required=False, type="list"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    api_endpoint = "locale-services"
    object_def = "locale-service"
    api_params_to_remove = ["resource_type"]

    api_protected_params = ["ha_mode", "transit_subnets", "internal_transit_subnets"]

    # Define params from ansible to remove for correct object as nsx api object
    ansible_params_to_remove = ["tier0"]

    manager_url = "https://{}/policy/api/v1/infra/tier-0s/{}".format(
        module.params["hostname"], module.params["tier0"]
    )

    nsx_module_execution(
        module=module,
        manager_url=manager_url,
        api_endpoint=api_endpoint,
        object_def=object_def,
        api_params_to_remove=api_params_to_remove,
        api_protected_params=api_protected_params,
        ansible_params_to_remove=ansible_params_to_remove,
    )


if __name__ == "__main__":
    main()
