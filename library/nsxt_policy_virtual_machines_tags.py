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

from ansible.module_utils.vmware_nsxt_policy_apis import vmware_argument_spec, request

import json, time

from ansible.module_utils._text import to_native

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: nsxt_policy_virtual_machines_tags

short_description: Manage a virtaul machines tags with policy APIS

description: >
    This module can be used to create, update or delete a tier1 gateway for NSX-T.
    To be able to delete a gateway, prior it's necessary to delete related objects to itself.

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
  virtual_machine:
    description: "Display name for concerned virtual machine"
    required: true
    type: str
  tags:
    description: "Keys values for tags"
    required: true
    type: list
    suboptions:
      scope:
      tag:
"""

EXAMPLES = """

nsxt_policy_virtual_machines_tags:
  hostname: "nsxvip.domain.local"
  username: "admin"
  password: "Vmware1!"
  validate_certs: false
  display_name: "My_first_virtual_machines_tags"
  virtual_machine: "myvmname"
  tags:
    - scope: string01
      tag: string01
"""

RETURN = """# """


def get_vm(vm_name, manager_url, mgr_username, mgr_password, validate_certs):
    my_vm = None
    try:
        headers = dict(Accept="application/json")
        headers["Content-Type"] = "application/json"
        (rc, resp) = request(
            url=manager_url,
            url_username=mgr_username,
            url_password=mgr_password,
            validate_certs=validate_certs,
            ignore_errors=True,
            headers=headers,
        )
    except Exception as err:
        module.fail_json(
            msg="Error getting  %s objects list. Error [%s]"
            % (object_def, to_native(err))
        )
    for vm in resp["results"]:
        if vm["display_name"] == vm_name:
            my_vm = vm
    if my_vm is not None:
        return my_vm
    else:
        return None


def update_tags(
    module, vm, manager_url, mgr_username, mgr_password, validate_certs, tags
):
    if module.check_mode:
        module.exit_json(
            changed=True, debug_out=str(json.dumps(params)), id=vm["display_name"]
        )

    try:
        headers = dict(Accept="application/json")
        headers["Content-Type"] = "application/json"
        params = {}
        params["tags"] = tags
        params["virtual_machine_id"] = vm["external_id"]
        request_data = json.dumps(params)

        (rc, resp) = request(
            url=manager_url,
            headers=headers,
            data=request_data,
            method="POST",
            url_username=mgr_username,
            url_password=mgr_password,
            validate_certs=validate_certs,
        )

    except Exception as err:
        module.fail_json(
            msg="Failed to create or update tags for virtual machine %s. Error[%s]."
            % (vm["display_name"], to_native(err))
        )

    time.sleep(5)

    module.exit_json(
        changed=True, message="Tags for vm %s or updated." % vm["display_name"]
    )


def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(
        virtual_machine=dict(required=True, type="str"),
        tags=dict(required=True, type="list"),
        enforcement_point=dict(required=False, type="str", default="default"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    base_url = "https://{}/policy/api/v1/infra/realized-state".format(
        module.params["hostname"]
    )
    get_vm_url = "{}/virtual-machines".format(base_url)
    post_url = "{}/enforcement-points/{}/virtual-machines?action=update_tags".format(
        base_url, module.params["enforcement_point"]
    )

    vm = get_vm(
        vm_name=module.params["virtual_machine"],
        manager_url=get_vm_url,
        mgr_username=module.params["username"],
        mgr_password=module.params["password"],
        validate_certs=module.params["validate_certs"],
    )

    if vm:
        if "tags" in vm:
            current_tags = sorted(vm["tags"], key=lambda tup: tup["tag"])
        else:
            current_tags = []
        needed_tags = sorted(module.params["tags"], key=lambda tup: tup["tag"])

        if str(current_tags) != str(needed_tags):
            update_tags(
                module=module,
                vm=vm,
                manager_url=post_url,
                mgr_username=module.params["username"],
                mgr_password=module.params["password"],
                validate_certs=module.params["validate_certs"],
                tags=module.params["tags"],
            )
        else:
            module.exit_json(
                changed=False,
                msg="Tags are already up-to-date for virtual machine %s"
                % (vm["display_name"]),
            )
    else:
        module.exit_json(
            failed=True,
            msg="Unkown virtual machine %s" % (module.params["virtual_machine"]),
        )


if __name__ == "__main__":
    main()
