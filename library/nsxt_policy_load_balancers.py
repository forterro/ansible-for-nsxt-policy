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
module: nsxt_policy_load_balancers
short_description: Manage NSX-T load_balancers  with policy APIS

description: Manage NSX-T load_balancers  with policy APIS

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
  connectivity_path:
    description:
      - "The connectivity target used to instantiate the LBService"
      - "LBS could be instantiated (or created) on the Tier-1, etc.
        For now, only the Tier-1 object is supported."
    required: false
    type: str
  enabled:
    description:
      - "Flag to enable the load balancer service."
    required: false
    type: bool
    default: true
  error_log_level:
    description:
      - "Load balancer engine writes information about encountered issues of
        different severity levels to the error log. This setting is used to
        define the severity level of the error log."
    required: false
    type: str
    choices:
      - DEBUG
      - INFO
      - WARNING
      - ERROR
      - CRITICAL
      - ALERT
      - EMERGENCY
    default: INFO
  size:
    description:
      - "Load balancer service size."
    required: false
    type: str:
    choices:
      - SMALL
      - MEDIUM
      - LARGE
      - DLB
    default: SMALL
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
nsxt_policy_load_balancers
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    display_name: "My_first_load_balancer"
    description: "My first load_balancer automated created by Ansible for NSX-T policy"

"""

RETURN = """# """


def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(
        display_name=dict(required=True, type="str"),
        description=dict(required=False, type="str"),
        state=dict(required=True, choices=["present", "absent"]),
        connectivity_path=dict(required=False, type="str"),
        enabled=dict(required=False, type="bool", default=True),
        error_log_level=dict(required=False, type="str", default="INFO"),
        access_log_enabled=dict(required=False, type="bool", default=False),
        size=dict(required=False, type="str", default="SMALL"),
        tags=dict(required=False, type="list"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    api_endpoint = "lb-services"  # Define API endpoint for object (eg: segments)
    object_def = "lb-service"  # Define object name (eg: segment)

    # Define api params to remove from returned object to get same object as ansible object
    api_params_to_remove = ["resource_type"]

    # Define read only params to fail module if call try to update
    api_protected_params = []

    # Define params from ansible to remove for correct object as nsx api object
    ansible_params_to_remove = []

    manager_url = "https://{}/policy/api/v1/infra".format(module.params["hostname"])

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
