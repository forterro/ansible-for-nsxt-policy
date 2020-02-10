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
module: nsxt_policy_segments_ports

short_description: Manage a segment_port with policy APIS (logical switch)

description: Manage a segment_port with policy APIS (logical switch)

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
    segment:
        description: "Display name for concerned segment"
        required: true
        type: str
    address_binding:
        description:
            - "Static address binding used for the port."
        type: list
        suboptions:
            ip_address:
                description: "IP Address for port binding"
                type: str
            mac_address:
                description: "Mac address for port binding"
                type: str
            vlan_id:
                description: "VLAN ID for port binding"
                type: int
    attachment:
        description: "Only VIF attachment is supported"
        type: dict
        suboptions:
            allocate_addresses:
                description: "Indicate how IP will be allocated for the port"
                type: str
                choices:
                    - IP_POOL
                    - MAC_POOL
                    - BOTH
                    - NONE
            app_id:
                description: "ID used to identify/look up a child attachment behind a parent attachment"
                type: str
            context_id:
                description: "Parent VIF ID if type is CHILD, Transport node ID if type is INDEPENDENT"
                type: str
            id:
                description: "VIF UUID on NSX Manager. If the attachement type is PARENT, this property is required."
                type: str
            traffic_tag:
                description: "Not valid when type is INDEPENDENT, mainly used to identify traffic from different
                            ports in container use case"
                type: int
            type:
                description: "Type of port attachment, it's an Enum value."
                type: str
                choices:
                    - PARENT
                    - CHILD
                    - INDEPENDENT
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
nsxt_policy_segments_ports:
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    display_name: "My_first_segments_ports"
    description: "My first segments_ports automated created by Ansible for NSX-T policy"


# Overlay routed segment
nsxt_policy_segments_ports:
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    display_name: "My_first_segments_ports"
    description: "My first segments_ports automated created by Ansible for NSX-T policy"
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
        segment=dict(required=True, type="str"),
        address_binding=dict(required=False, type="list"),
        attachment=dict(required=False, type="dict"),
        tags=dict(required=False, type="list"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True,)

    api_endpoint = "ports"
    object_def = "port"

    api_params_to_remove = ["resource_type"]
    api_protected_params = []
    ansible_params_to_remove = ["segment"]

    manager_url = "https://{}/policy/api/v1/infra/segments/{}".format(
        module.params["hostname"], module.params["segment"]
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
