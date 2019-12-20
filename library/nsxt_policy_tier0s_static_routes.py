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
module: nsxt_policy_tier0s_static_routes

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
    required: true
    type: str
  description:
    description: Description
    required: false
    type: str
  tier0:
    description: Identifier for concerned tier0 (display_name)
    required: true
    type: str
  network:
    description:    Network address in CIDR format
                    Specify network address in CIDR format.
    required: true
    type: str
  next_hops:
    description:    Next hop routes for network
                    Minimum items: 1
                    - ip_address:
                        description: Next hop gateway IP address
                        required: true
                        type: str
                      admin_distance:
                        description:  Cost associated with next hop route
                        required: true
                        type: int
    required: true
    type: list
"""

EXAMPLES = """

nsxt_policy_tier0s_static_routes:
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    display_name: "external"
    description: "My first tier0s_static_routes automated created by Ansible for NSX-T policy"
    tier0: "my_tier0"
    network: 10.100.0.0/26
    next_hops:
        - ip_address: 10.1.1.1
          admin_distance: 1
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
        display_name=dict(required=True, type="str"),
        description=dict(required=False, type="str"),
        state=dict(required=True, choices=["present", "absent"]),
        tier0=dict(required=True, type="str"),
        network=dict(required=True, type="str"),
        next_hops=dict(required=False, type="list"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    api_endpoint = "static-routes"
    object_def = "static-route"
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
