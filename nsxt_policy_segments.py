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
module: nsxt_policy_segments

short_description: Manage a segment with api policy (logical switch)

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
'''

EXAMPLES = '''

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

'''


RETURN = '''# '''

import json, time
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.vmware_nsxt import vmware_argument_spec, request
from ansible.module_utils._text import to_native


# Remove vmware_nsxt module util parameters and return specific params for this nsx-t module
def get_nsx_module_params(args=None):
    args_to_remove = ['state', 'username', 'password', 'port', 'hostname', 'validate_certs','display_name']
    for key in args_to_remove:
        args.pop(key, None)
    for key, value in args.copy().items():
        if value == None:
            args.pop(key, None)
    return args

# Remove unecessary api params to have similar object between ansible and api
def remove_api_params(object,params_to_remove):
    for key in params_to_remove:
        object.pop(key, None)
    for key, value in object.copy().items():
        if value == None:
            object.pop(key, None)
    return object

# Get all nsx-t objects for current api endpoint
def get_nsx_objects(module, manager_url, api_endpoint, mgr_username, mgr_password, validate_certs,object_def):
    try:
      (rc, resp) = request( url=manager_url+ '/' + api_endpoint,
                            headers=dict(Accept='application/json'),
                            url_username=mgr_username,
                            url_password=mgr_password,
                            validate_certs=validate_certs,
                            ignore_errors=True
                          )
    except Exception as err:
      module.fail_json(msg='Error getting  %s objects list. Error [%s]' % (object_def,to_native(err)))
    return resp

# Get nsx-t object with display name
def get_nsx_object(module, manager_url, api_endpoint, mgr_username, mgr_password, validate_certs, display_name,object_def):
    objects = get_nsx_objects(  module=module,
                                manager_url=manager_url,
                                api_endpoint=api_endpoint,
                                mgr_username=mgr_username,
                                mgr_password=mgr_password,
                                validate_certs=validate_certs,
                                object_def=object_def
                              )
    for object in objects['results']:
        if object.__contains__('display_name') and object['display_name'] == display_name:
            return object
    return None

# Check if object must be updated
def check_for_update(module, object, params, params_to_remove,protected_params):
  clean_object = remove_api_params(object=object,params_to_remove=params_to_remove)

  for key in protected_params:
    if (clean_object.__contains__(key) and not params.__contains__(key)) or \
       (not clean_object.__contains__(key) and params.__contains__(key)) or \
       (clean_object.__contains__(key) and params.__contains__(key) and clean_object[key] != params[key]):
       module.fail_json(msg="Parameter %s is protected. You cannot update this attribute." % (key))

  if json.dumps(clean_object, sort_keys=True) != json.dumps(params, sort_keys=True):
    return True
  return False

def create_or_update_nsx_object(module, manager_url, api_endpoint, mgr_username, mgr_password, validate_certs, params,display_name,object_def):
    if module.check_mode:
        module.exit_json(changed=True, debug_out=str(json.dumps(params)), id=display_name)
    try:
      headers = dict(Accept="application/json")
      headers['Content-Type'] = 'application/json'
      request_data = json.dumps(params)
      (rc, resp) = request( url=manager_url + "/" + api_endpoint+ "/%s" % display_name,
                            headers=headers,
                            data=request_data,
                            method='PATCH',
                            url_username=mgr_username,
                            url_password=mgr_password,
                            validate_certs=validate_certs
                          )
    except Exception as err:
      module.fail_json(msg="Failed to create or update %s with name %s. Error[%s]." % (object_def,display_name, to_native(err)))

    time.sleep(5)
    module.exit_json( changed=True,
                      object_name=display_name,
                      message="%s with name %s created or updated." % (object_def,display_name)
                    )

def delete_nsx_object(module, manager_url, api_endpoint, mgr_username, mgr_password, validate_certs, display_name,object_def):
    if module.check_mode:
        module.exit_json(changed=True, debug_out=str(id=display_name))
    try:
        (rc, resp) = request( url=manager_url + "/" + api_endpoint+ "/%s" % display_name,
                              method='DELETE',
                              url_username=mgr_username,
                              url_password=mgr_password,
                              validate_certs=validate_certs
                            )
    except Exception as err:
        module.fail_json(msg="Failed to delete %s with name %s. Error[%s]." % (object_def,display_name, to_native(err)))

    time.sleep(5)
    module.exit_json( changed=True,
                      object_name=display_name,
                      message="%s with name %s deleted." % (object_def,display_name)
                    )

def main():
  argument_spec = vmware_argument_spec()
  argument_spec.update( display_name=dict(required=True, type='str'),
                        description=dict(required=False, type='str'),
                        state=dict(required=True, choices=['present', 'absent']),
                        vlan_ids=dict(required=False, type='list'),
                        connectivity_path=dict(required=False,type='str'),
                        transport_zone_path=dict(required=True, type='str'),
                        advanced_config=dict(required=False, type='dict'),
                        subnets=dict(required=False, type='list'),
                        domain_name=dict(required=False, type='str')
                      )

  #
  #  Beginning of module configuration block
  #
  api_endpoint    = 'segments'
  object_def      = 'segment'
  api_params_to_remove =  [
                            'display_name',
                            'type',
                            'marked_for_delete',
                            'resource_type',
                            'id',
                            'path',
                            'parent_path',
                            'relative_path',
                            '_create_user',
                            '_create_time',
                            '_last_modified_user',
                            '_last_modified_time',
                            '_system_owned',
                            '_protection',
                            '_revision'
                          ]

  api_protected_params =  [
                            'transport_zone_path'
                          ]

  #
  # End of module configuration block
  #

  #
  # Begining of parameters block
  #
  module = AnsibleModule( argument_spec=argument_spec,
                          supports_check_mode=True,
                          mutually_exclusive=[
                            ['vlan_ids', 'connectivity_path'],
                            ['vlan_ids', 'subnets']
                          ]
                        )

  state           = module.params['state']
  mgr_hostname    = module.params['hostname']
  mgr_username    = module.params['username']
  mgr_password    = module.params['password']
  validate_certs  = module.params['validate_certs']
  display_name    = module.params['display_name']
  manager_url     = 'https://{}/policy/api/v1/infra'.format(mgr_hostname)

  nsx_module_params = get_nsx_module_params(module.params.copy())

  # update advanced config
  if (nsx_module_params.__contains__('advanced_config')):
    nsx_module_params['advanced_config']['hybrid'] = False
    nsx_module_params['advanced_config']['local_egress'] = False
    nsx_module_params['advanced_config']['connectivity'] = "ON"

  #
  # End of parameters block
  #

  # Search for nsx object
  nsx_object = get_nsx_object(  module=module,
                                manager_url=manager_url,
                                api_endpoint=api_endpoint,
                                mgr_username=mgr_username,
                                mgr_password=mgr_password,
                                validate_certs=validate_certs,
                                display_name=display_name,
                                object_def=object_def
                              )

  # Present state
  if state == 'present':

    # If object already exists, check for update
    if nsx_object:
      to_update = check_for_update( module=module,
                                    object=nsx_object,
                                    params=nsx_module_params,
                                    params_to_remove=api_params_to_remove,
                                    protected_params=api_protected_params
                                  )

    # Create or update NSX object
    if (not nsx_object or to_update):
      create_or_update_nsx_object(  module=module,
                                    manager_url=manager_url,
                                    api_endpoint=api_endpoint,
                                    mgr_username=mgr_username,
                                    mgr_password=mgr_password,
                                    validate_certs=validate_certs,
                                    params=nsx_module_params,
                                    display_name=display_name,
                                    object_def=object_def
                                  )
    else:
      module.exit_json(changed=False, msg='%s with display name %s is up to date' % (object_def,display_name))

  # Absent state
  if state == 'absent':
    if nsx_object:
      delete_nsx_object(module=module,
                                manager_url=manager_url,
                                api_endpoint=api_endpoint,
                                mgr_username=mgr_username,
                                mgr_password=mgr_password,
                                validate_certs=validate_certs,
                                display_name=display_name,
                                object_def=object_def

      )
    else:
      module.exit_json(changed=False, msg='No %s exist with display name %s' % (object_def,display_name))

if __name__ == '__main__':
    main()