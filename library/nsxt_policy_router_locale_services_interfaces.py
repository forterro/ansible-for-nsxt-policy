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

from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.vmware_nsxt_policy_apis import (
    vmware_argument_spec,
    nsx_module_execution,
)

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: nsxt_policy_router_locale_services_interfaces

short_description: Manage a tier0 or tier 1 locale service interface with policy APIS

description: Manage a tier0 or tier 1 locale service interface with policy APIS

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
    description:
      - "Identifier to use when displaying entity in logs or GUI"
      - "Maximum length: 255"
    required: false
    type: str
    default: default
  description:
    description: Description
    required: false
    type: str
  tier0:
    description: "Identifier for concerned tier0 (display_name), mutually exclusive with tier1"
    required: true
    type: str
  tier1:
    description: "Identifier for concerned tier1 (display_name), mutually exclusive with tier0"
    required: true
    type: str
  locale_service:
    description: Identifier for concerned locale service
    required: true
    type: str
  ipv6_profile_paths:
    description:
      - "Configuration IPv6 NDRA profile. Only one NDRA profile can be configured."
      - "Minimum items: 0"
      - "Maximum items: 1"
    required: false
    default:
      - "/infra/ipv6-ndra-profiles/default"
    type: list
  mtu:
    description:  "Maximum transmission unit (MTU) specifies the size of the largest
                  packet that a network protocol can transmit."
    required: false
    type: int
  segment_path:
    description:  Specify Segment to which this interface is connected to.
    required: true
    type: str
  subnets:
    required: true
    type: list
    description:  Specify IP address and network prefix for interface.
    suboptions:
      ip_addresses:
        description: IP addresses assigned to interface
        type: list
        required: true
      prefix_len:
        description: Subnet prefix length
        type: list
        required: true
  edge_path:
    description:
      - "Policy path to edge node to handle external connectivity."
      - "Required when interface type is EXTERNAL."
      - "Only for tier0 interface"
    required: False
    type: str
  type:
    description:
      - "Interface type"
      - "Only for tier0 interface"
    required: false
    type: str
    choices:
      - EXTERNAL
      - SERVICE
      - LOOPBACK
    default: EXTERNAL
  tags:
      description:
          - "Opaque identifiers meaningful to the API user"
          - "Maximum items : 30"
      type: list
      suboptions:
          scope:
              description: "Tag searches may optionally be restricted by scope"
              required: false
              type: str
          tag:
              description: "Identifier meaningful to user with maximum length of 256 characters"
              required: true
              type: str

"""

EXAMPLES = """

nsxt_policy_router_locale_services_interfaces:
  hostname: "nsxvip.domain.local"
  username: "admin"
  password: "Vmware1!"
  validate_certs: false
  display_name: "My_first_router_locale_services_interfaces"
  description: "My first router_locale_services_interfaces automated created by Ansible for NSX-T policy"
  tier0: "my_tier0"
  edge_cluster_path: "/infra/sites/default/enforcement-points/default/edge-clusters/b0181f39-24e6-455c-a1d8-7c65e9abe7ae",
  preferred_edge_paths: "/infra/sites/default/enforcement-points/default/edge-clusters/b0181f39-24e6-455c-a1d8-7c65e9abe7ae/edge-nodes/b2236f0f-295f-47f8-a37c-f42139083c49"

"""


RETURN = """# """


def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(
        display_name=dict(required=False, type="str", default="default"),
        description=dict(required=False, type="str"),
        state=dict(required=True, choices=["present", "absent"]),
        tier0=dict(required=False, type="str"),
        tier1=dict(required=False, type="str"),
        locale_service=dict(required=True, type="str"),
        ipv6_profile_paths=dict(
            required=False, type="list", default=["/infra/ipv6-ndra-profiles/default"]
        ),
        mtu=dict(required=False, type="int"),
        segment_path=dict(required=True, type="str"),
        subnets=dict(required=True, type="list"),
        edge_path=dict(required=False, type="str"),
        type=dict(
            required=False,
            type="str",
            choices=["EXTERNAL", "SERVICE", "LOOPBACK"],
            default="EXTERNAL",
        ),
        tags=dict(required=False, type="list"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[["tier0", "tier1"]],
    )

    api_endpoint = "interfaces"
    object_def = "interface"
    api_params_to_remove = []

    api_protected_params = []

    # Define params from ansible to remove for correct object as nsx api object
    ansible_params_to_remove = ["locale_service", "tier0", "tier1"]

    if module.params["tier0"]:
        manager_url = "https://{}/policy/api/v1/infra/tier-0s/{}/locale-services/{}".format(
            module.params["hostname"],
            module.params["tier0"],
            module.params["locale_service"],
        )
        module.params["resource_type"] = "Tier0Interface"
        ansible_params_to_remove += ["type"]
    elif module.params["tier1"]:
        manager_url = "https://{}/policy/api/v1/infra/tier-1s/{}/locale-services/{}".format(
            module.params["hostname"],
            module.params["tier1"],
            module.params["locale_service"],
        )
        module.params["resource_type"] = "Tier1Interface"
        ansible_params_to_remove += ["type", "edge_path"]
    else:
        module.fail_json(msg="Missing parameter tier0 or tier1")

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
