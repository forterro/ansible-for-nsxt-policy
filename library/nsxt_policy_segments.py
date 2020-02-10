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
    get_nsx_module_params,
)

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: nsxt_policy_segments

short_description: Manage a segment with policy APIS (logical switch)

description: Manage a segment with policy APIS (logical switch)

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
        description:
            - "State can be either 'present' or 'absent'."
            - "'present' is used to create or update resource."
            - "'absent' is used to delete resource."
        required: true
        type: str
    display_name:
        description:
            - "Identifier to use when displaying entity in logs or GUI"
            - "Maximum length 255"
        required: true
        type: str
    description:
        description:
            - "Description"
        required: false
        type: str
    vlan_ids:
        description:
            - "VLAN ids for a VLAN backed Segment."
            - "Can be a VLAN id or a range of VLAN ids specified with '-' in between."
        required: false
        type: list
        elements: str
    connectivity_path:
        description:
            - "Policy path to the connecting Tier-0 or Tier-1."
            - "Valid only for segments created under Infra."
        required: false
        type: str
    transport_zone_path:
        description:
            - "Policy path to the transport zone. Supported for VLAN backed segments as well as Overlay Segments."
            - "This field is required for VLAN backed Segments."
            - "Auto assigned if only one transport zone exists in the enforcement point."
            - "Default transport zone is auto assigned for overlay segments if none specified."
        required: false
        type: str
    advanced_config:
        required: false
        type: dict
        description: "Advanced configuration for Segment."
        suboptions:
            address_pool_paths:
                description:
                    - "Policy path to IP address pools."
                    - "Maximum items: 1"
                required: false
                type: list
                elements: str
            connectivity:
                description:
                    - "Connectivity configuration to manually connect (ON) or disconnect (OFF)
                        a logical entity from network topology."
                required: false
                type: str
                choices:
                    - "ON"
                    - "OFF"
                default: "ON"
            hybrid:
                description:
                    - "Flag to identify a hybrid logical switch"
                    - "When set to true, all the ports created on this segment will behave
                        in a hybrid fashion. The hybrid port indicates to NSX that the
                        VM intends to operate in underlay mode, but retains the ability to
                        forward egress traffic to the NSX overlay network."
                    - "This property is only applicable for segment created with transport
                        zone type OVERLAY_STANDARD."
                    - "This property cannot be modified after segment is created."
                type: boolean
                default: false
            local_egress:
                description:
                    - "This property is used to enable proximity routing with local egress.
                        When set to true, logical router interface (downlink) connecting
                        Segment to Tier0/Tier1 gateway is configured with prefix-length 32.3"
                type: boolean
                default: false

    subnets:
        required: false
        type: list
        description:
            - "Only for overlay segments"
            - "Max 1 subnet"
        suboptions:
            gateway_address:
                description:
                    - "Gateway IP address in CIDR format for both IPv4 and IPv6."
                type: str
                required: true
            network:
                description:
                    - "Network CIDR for this subnet calculated from gateway_addresses and prefix_len"
                type: str
                required: true
            dhcp_ranges:
                description:
                    - "DHCP address ranges are used for dynamic IP allocation."
                    - "Supports address range and CIDR formats. First valid
                        host address from the first value is assigned to DHCP server
                        IP address. Existing values cannot be deleted or modified,
                        but additional DHCP ranges can be added."
                    - "Minimum item: 1"
                required: false
                type: list
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
        tags=dict(required=False, type="list"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[["vlan_ids", "connectivity_path"], ["vlan_ids", "subnets"]],
    )

    api_endpoint = "segments"
    object_def = "segment"

    api_params_to_remove = ["resource_type", "type"]
    api_protected_params = ["transport_zone_path"]
    ansible_params_to_remove = []

    manager_url = "https://{}/policy/api/v1/infra".format(module.params["hostname"])

    # update advanced config
    if module.params.__contains__("advanced_config"):
        module.params["advanced_config"] = {}
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
