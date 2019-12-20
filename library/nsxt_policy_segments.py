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
module: nsxt_policy_segments

short_description: Manage a segment with policy APIS (logical switch)

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
        description: "State can be either 'present' or 'absent'.
                    'present' is used to create or update resource.
                    'absent' is used to delete resource."
        required: true
    display_name:
        description: Display name
        required: true
        type: str
    description:
        description: Description
        required: false
        type: str
    vlan_ids:
        description: list of vlans or vlan ranges to be associated.
                     Mutually exclusive with subnets and connectivity_path.
                     Make sure associated transport zone is vlan zone.
        required: false
        type: list
    connectivity_path:
        description: path (formely /infra/tier-0s/<name> or /infra/tier-1s/<name>) of router
        required: false
        type: str
    transport_zone_path:
        description: path (formely /infra/sites/default/enforcement-points/default/transport-zones/<id>) for transport zone.
                     Be sure transport zone type is accorded to segment type (vlan or overlay)
        required: true
        type: str
    advanced_config
        required: false
        type: dict
        description:
            Attributes are:
                - address_pool_paths (list): path for ippool min(0) - max(1)
    subnets:
        required: false
        type: list
        description:
            Only for overlay segments
            Max 1 subnet
            attributes:
                - gateway_address (str)(required) CIDR format xxx.xxx.xxx.xxx/yy
                  network  (str)(required) CIDR format xxx.xxx.xxx.xxx/yy
                  dhcp_ranges: array of ipElement. Need to configure dhcp on connected routed
"""

EXAMPLES = """

# Vlan Backed segment
nsxt_policy_segments:
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    display_name: "My_first_segments"
    description: "My first segments automated created by Ansible for NSX-T policy"
    vlan_ids:
        - 100-120
        - 200
    transport_zone_path: "/infra/sites/default/enforcement-points/default/transport-zones/e0de84fc-9438-4603-b8fd-306624b1b18c"  # VLAN transport zone
    advanced_config:
      address_pool_paths:
        - "/infra/ip-pools/ippool-test"

# Overlay routed segment
nsxt_policy_segments:
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    display_name: "My_first_segments"
    description: "My first segments automated created by Ansible for NSX-T policy"
    transport_zone_path: "/infra/sites/default/enforcement-points/default/transport-zones/e0de84fc-9438-4603-b8fd-306624b1b18c"  # Overlay transport zone
    connectivity_path : "/infra/tier-0s/tier0-test"
    subnets:
        - gateway_address: "10.120.123.2/24"
          network: "10.120.123.0/24"
          dhcp_ranges:
            - 10.120.123.10-10.120.123.20
            - 10.120.123.100-10.120.123.200
    advanced_config:
      address_pool_paths:
        - "/infra/ip-pools/ippool-overlay1"

"""


RETURN = """# """

from ansible.module_utils.vmware_nsxt_policy_apis import (
    vmware_argument_spec,
    nsx_module_execution,
    get_nsx_module_params,
)
from ansible.module_utils.basic import AnsibleModule


def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(
        display_name=dict(required=True, type="str"),
        description=dict(required=False, type="str"),
        state=dict(required=True, choices=["present", "absent"]),
        vlan_ids=dict(required=False, type="list"),
        connectivity_path=dict(required=False, type="str"),
        transport_zone_path=dict(required=True, type="str"),
        advanced_config=dict(required=False, type="dict"),
        subnets=dict(required=False, type="list"),
        domain_name=dict(required=False, type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[["vlan_ids", "connectivity_path"], ["vlan_ids", "subnets"]],
    )

    api_endpoint = "segments"
    object_def = "segment"

    api_params_to_remove = ["resource_type"]
    api_protected_params = ["transport_zone_path"]
    ansible_params_to_remove = []

    manager_url = "https://{}/policy/api/v1/infra".format(module.params["hostname"])

    # update advanced config
    if module.params.__contains__("advanced_config"):
        module.params["advanced_config"]["hybrid"] = False
        module.params["advanced_config"]["local_egress"] = False
        module.params["advanced_config"]["connectivity"] = "ON"

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
