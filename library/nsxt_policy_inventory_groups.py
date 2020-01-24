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
module: nsxt_policy_inventory_groups

short_description: Manage NSX-T inventory groups with policy APIS

description: Manage NSX-T inventory groups with policy APIS

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
    domain:
        description: Display name domain
        required: false
        default: default
        type: str
    expression:
        description:
            - "The expression list must follow below criteria:"
            - "1. A non-empty expression list, must be of odd size. In a list, with
                indices starting from 0, all non-conjunction expressions must be at
                even indices, separated by a conjunction expression at odd
                indices."
            - "2. The total of ConditionExpression and NestedExpression in a list
                should not exceed 5."
            - "3. The total of IPAddressExpression, MACAddressExpression, external
                IDs in an ExternalIDExpression and paths in a PathExpression must not exceed
                500."
            - "4. Each expression must be a valid Expression. See the definition of
                the Expression type for more information."
        type: list
        required: false
        suboptions:
            description:
                description: "Description of this resource"
                required: false
                type: str
            display_name:
                description: " 	Identifier to use when displaying entity in logs or GUI"
                required: false
                type: str

"""

EXAMPLES = """
nsxt_policy_inventory_groups:
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    display_name: "My_first_ippool_static_subnet"
    description: "My first inventory_groups automated created by Ansible for NSX-T policy"

"""

RETURN = """# """


def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(
        display_name=dict(required=True, type="str"),
        description=dict(required=False, type="str"),
        state=dict(required=True, choices=["present", "absent"]),
        domain=dict(required=False, type="str", default="default"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    api_endpoint = "groups"  # Define API endpoint for object (eg: segments)
    object_def = "group"  # Define object name (eg: segment)

    # Define api params to remove from returned object to get same object as ansible object
    api_params_to_remove = []

    # Define read only params to fail module if call try to update
    api_protected_params = []

    # Define params from ansible to remove for correct object as nsx api object
    ansible_params_to_remove = []

    manager_url = "https://{}/policy/api/v1/infra/domains/{}".format(
        module.params["hostname"], module.params["domain"]
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
