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
module: nsxt_policy_lb_tcp_monitor_profiles
short_description: Manage NSX-T lb_tcp_monitor_profiles  with policy APIS

description: Manage NSX-T lb_tcp_monitor_profiles  with policy APIS

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
  fall_count:
    description:
      -  "Only if a healthcheck fails consecutively for a specified number of
          times, given with fall_count, to a member will the member status be
          marked DOWN."
    required:false
    type: int
    default: 3
  interval:
    description:
      -  "Active healthchecks are initiated periodically, at a configurable interval (in seconds), to each member of the Group."
    required:false
    type: int
    default: 5
  monitor_port:
    description:
      -  "Typically, monitors perform healthchecks to Group members using the member IP address and pool_port. However, in some cases, customers prefer to run healthchecks against a different port than the pool member port which handles actual application traffic. In such cases, the port to run healthchecks against can be specified in the monitor_port value. For ICMP monitor, monitor_port is not required."
    required:false
    type: int
  receive:
    description:
      -  "Expected data, if specified, can be anywhere in the response and it has to be a string, regular expressions are not supported."
    required:false
    type: str
  rise_count:
    description:
      - "Once a member is DOWN, a specified number of consecutive successful healthchecks specified by rise_count will bring the member back to UP state."
    required:false
    type: int
    default: 3
  send:
    description:
      -  "If both send and receive are not specified, then just a TCP connection is established (3-way handshake) to validate server is healthy, no data is sent."
    required:false
    type: str
  timeout:
    description:
      - "Timeout specified in seconds.  After a healthcheck is initiated, if it does not complete within a certain period, then also the healthcheck is considered to be unsuccessful. Completing a healthcheck within timeout means establishing a connection (TCP or SSL), if applicable, sending the request and receiving the response, all within the configured timeout."
    required:false
    type: int
    default: 3
"""

EXAMPLES = """
nsxt_policy_lb_tcp_monitor_profiles
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    display_name: "My_first_ippool"
    description: "My first lb_tcp_monitor_profiles automated created by Ansible for NSX-T policy"
"""

RETURN = """# """


def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(
        display_name=dict(required=True, type="str"),
        description=dict(required=False, type="str"),
        state=dict(required=True, choices=["present", "absent"]),
        fall_count=dict(required=False, type="int", default=3),
        interval=dict(required=False, type="int", default=5),
        monitor_port=dict(required=False, type="int"),
        receive=dict(required=False, type="str"),
        rise_count=dict(required=False, type="int", default=3),
        send=dict(required=False, type="str"),
        timeout=dict(required=False, type="int", default=15),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    api_endpoint = (
        "lb-monitor-profiles"  # Define API endpoint for object (eg: segments)
    )
    object_def = "lb-monitor-profile"  # Define object name (eg: segment)

    # Define api params to remove from returned object to get same object as ansible object
    api_params_to_remove = []

    # Define read only params to fail module if call try to update
    api_protected_params = []

    # Define params from ansible to remove for correct object as nsx api object
    ansible_params_to_remove = []

    manager_url = "https://{}/policy/api/v1/infra".format(module.params["hostname"])

    module.params["resource_type"] = "LBTcpMonitorProfile"

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
