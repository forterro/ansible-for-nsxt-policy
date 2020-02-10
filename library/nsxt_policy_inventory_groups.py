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
            - "See examples below to use expressions
            - "Documentations for expression types"
            - "Condition : https://vdc-download.vmware.com/vmwb-repository/dcr-public/6c24b5c0-396a-4152-9125-bd10a795836b/74043a09-7320-40ac-ac85-9416d0f9cd01/nsx_25_api.html#Type.Condition"
            - "ConjunctionOperator : https://vdc-download.vmware.com/vmwb-repository/dcr-public/6c24b5c0-396a-4152-9125-bd10a795836b/74043a09-7320-40ac-ac85-9416d0f9cd01/nsx_25_api.html#Type.Condition"
            - "ExternalIDExpression : https://vdc-download.vmware.com/vmwb-repository/dcr-public/6c24b5c0-396a-4152-9125-bd10a795836b/74043a09-7320-40ac-ac85-9416d0f9cd01/nsx_25_api.html#Type.ExternalIDExpression"
            - "IPAddressExpression : https://vdc-download.vmware.com/vmwb-repository/dcr-public/6c24b5c0-396a-4152-9125-bd10a795836b/74043a09-7320-40ac-ac85-9416d0f9cd01/nsx_25_api.html#Type.IPAddressExpression"
            - "IdentityGroupExpression : https://vdc-download.vmware.com/vmwb-repository/dcr-public/6c24b5c0-396a-4152-9125-bd10a795836b/74043a09-7320-40ac-ac85-9416d0f9cd01/nsx_25_api.html#Type.IdentityGroupExpression"
            - "MACAddressExpression : https://vdc-download.vmware.com/vmwb-repository/dcr-public/6c24b5c0-396a-4152-9125-bd10a795836b/74043a09-7320-40ac-ac85-9416d0f9cd01/nsx_25_api.html#Type.MACAddressExpression"
            - "NestedExpression : https://vdc-download.vmware.com/vmwb-repository/dcr-public/6c24b5c0-396a-4152-9125-bd10a795836b/74043a09-7320-40ac-ac85-9416d0f9cd01/nsx_25_api.html#Type.NestedExpression"
            - "PathExpression : https://vdc-download.vmware.com/vmwb-repository/dcr-public/6c24b5c0-396a-4152-9125-bd10a795836b/74043a09-7320-40ac-ac85-9416d0f9cd01/nsx_25_api.html#Type.PathExpression"
        type: list
        required: false
    extended_expression:
        description:
            - "Extended Expression allows additional higher level context to be
                specified for grouping criteria. (e.g. user AD group)
                This field allow users to specified user context as the source of a
                firewall rule for IDFW feature.
                Current version only support a single IdentityGroupExpression. In the
                future, this might expand to support other conjunction and non-conjunction
                expression."

            - "The extended expression list must follow below criteria:"
            - "1. Contains a single IdentityGroupExpression. No conjunction expression is
            supported.3
            - "2. No other non-conjunction expression is supported, except for
            IdentityGroupExpression."
            - "3. Each expression must be a valid Expression. See the definition of
            the Expression type for more information."
            - "4. Extended expression are implicitly AND with expression."
            - "5. No nesting can be supported if this value is used."
            - "6. If a Group is using extended expression, this group must be the only
            member in the source field of an communication map."
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
nsxt_policy_inventory_groups:
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    display_name: "My_first_ippool_static_subnet"
    description: "My first inventory_groups automated created by Ansible for NSX-T policy"
    expression:
        - member_type: "VirtualMachine"
          value: "role|webvm"
          key: "Tag"
          operator: "EQUALS"
          resource_type: "Condition"
        - resource_type: "ConjunctionOperator"
          conjunction_operator: "OR"
        - member_type: "VirtualMachine"
          value: "scope|value"
          key: "Tag"
          operator: "EQUALS"
          resource_type: "Condition"
      }
    ]
"""

RETURN = """# """


def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(
        display_name=dict(required=True, type="str"),
        description=dict(required=False, type="str"),
        state=dict(required=True, choices=["present", "absent"]),
        domain=dict(required=False, type="str", default="default"),
        expression=dict(required=False, type="list"),
        extended_expression=dict(required=False, type="list"),
        tags=dict(required=False, type="list"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    api_endpoint = "groups"  # Define API endpoint for object (eg: segments)
    object_def = "group"  # Define object name (eg: segment)

    # Define api params to remove from returned object to get same object as ansible object
    api_params_to_remove = ["resource_type"]

    # Define read only params to fail module if call try to update
    api_protected_params = []

    # Define params from ansible to remove for correct object as nsx api object
    ansible_params_to_remove = ["domain"]

    # Update expression object for indempotence
    if "expression" in module.params and bool(module.params["expression"]):
        for member in module.params["expression"]:
            member["_protection"] = "NOT_PROTECTED"
            member["marked_for_delete"] = False

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
