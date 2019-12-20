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
module: nsxt_policy_ippools_static_subnets_facts

short_description: Get NSX-T ippools_static_subnets facts from policy APIS

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
    ippool:
        description: Display name for targeted ippool
        required: true
        type: str
"""

EXAMPLES = """

# Returns facts for one ippool
nsxt_policy_ippools_static_subnets_facts:
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    display_name: "My_first_ippool_static_subnet"
    ippool: "My_first_ippool"
register: nsxt_ippool_static_subnet

# Returns facts for all ippools_static_subnets
nsxt_policy_ippools_static_subnets_facts:
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    ippool: "My_first_ippool"

register: nsxt_ippools_static_subnets

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
        ippool=dict(required=True, type="str"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    api_endpoint = "ip-subnets"  # Define API endpoint for object (eg: segments)
    object_def = "ip-subnet"  # Define object name (eg: segment)
    manager_url = "https://{}/policy/api/v1/infra/ip-pools/{}".format(
        module.params["hostname"], module.params["ippool"]
    )

    nsx_module_facts_execution(
        module=module,
        manager_url=manager_url,
        api_endpoint=api_endpoint,
        object_def=object_def,
    )


if __name__ == "__main__":
    main()
