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


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: nsxt_policy_ippools

short_description: Empty template to allows to develop quickly modules for nsx-t api policy

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
'''

EXAMPLES = '''
nsxt_policy_ippools:
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    display_name: "My_first_ippool"
    description: "My first ippools automated created by Ansible for NSX-T policy"
'''

RETURN = '''# '''

from ansible.module_utils.vmware_nsxt_policy_apis import vmware_argument_spec,nsx_module_execution,get_nsx_module_params
from ansible.module_utils.basic import AnsibleModule

def main():
  argument_spec = vmware_argument_spec()
  argument_spec.update( display_name=dict(required=True, type='str'),
                        description=dict(required=False, type='str'),
                        state=dict(required=True, choices=['present', 'absent'])
                      )

  module = AnsibleModule( argument_spec=argument_spec, supports_check_mode=True)

  api_endpoint    = 'ip-pools'   # Define API endpoint for object (eg: segments)
  object_def      = 'ip-pool'   # Define object name (eg: segment)

  # Define api params to remove from returned object to get same object as ansible object
  api_params_to_remove =  ['resource_type']

  # Define read only params to fail module if call try to update
  api_protected_params =  []

  # Define params from ansible to remove for correct object as nsx api object
  ansible_params_to_remove = []

  manager_url     = 'https://{}/policy/api/v1/infra'.format(module.params['hostname'])

  nsx_module_execution( module=module,
                        manager_url=manager_url,
                        api_endpoint=api_endpoint,
                        object_def=object_def,
                        api_params_to_remove=api_params_to_remove,
                        api_protected_params=api_protected_params,
                        ansible_params_to_remove=ansible_params_to_remove
                      )


if __name__ == '__main__':
    main()