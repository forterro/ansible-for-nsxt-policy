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
module: nsxt_policy_tier0s_static_routes_facts

short_description: Get NSX-T tier0s_static_routes facts from policy APIS

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
    display_name:
        description: Display name
        required: false
        type: str
    tier0:
        description: Identifier for concerned tier0 (display_name)
        required: true
        type: str
"""

EXAMPLES = """

# Returns facts for one tier0
nsxt_policy_tier0s_static_routes_facts:
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    display_name: "My_first_tier0s_static_routes"
    tier0: "my_tier0"
register: nsxt_tier0

# Returns facts for all tier0s_static_routes
nsxt_policy_tier0s_static_routes_facts:
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    tier0: "my_tier0"
register: nsxt_tier0s_static_routes

"""


RETURN = """# """

from ansible.module_utils.vmware_nsxt_policy_apis import (
    vmware_argument_spec,
    nsx_module_facts_execution,
)
from ansible.module_utils.basic import AnsibleModule


def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(
        display_name=dict(required=False, type="str"),
        tier0=dict(required=True, type="str"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    api_endpoint = "static-routes"
    object_def = "static-route"
    manager_url = "https://{}/policy/api/v1/infra/tier-0s/{}".format(
        module.params["hostname"], module.params["tier0"]
    )

    nsx_module_facts_execution(
        module=module,
        manager_url=manager_url,
        api_endpoint=api_endpoint,
        object_def=object_def,
    )


if __name__ == "__main__":
    main()
