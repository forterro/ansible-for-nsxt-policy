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

from ansible.module_utils.vmware_nsxt_policy_apis import (
    vmware_argument_spec,
    nsx_module_execution,
)
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: nsxt_policy_tier1s

short_description: Manage a tier1 with policy APIS (logical north south router)

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
  dhcp_config_paths:
    description:  DHCP configuration for Segments connected to Tier-0
                  DHCP configuration for Segments connected to Tier-0.
                  DHCP service is configured in relay mode.
                  Minimum items: 0
                  Maximum items: 1
    required: false
    type: list
  disable_firewall:
    description: Disable or enable gateway fiewall.
    required: false
    default: false
    type: bool
  enable_standby_relocation:
    description:  Flag to enable standby service router relocation.
                  Standby relocation is not enabled until edge cluster is configured
                  for Tier1.
    required: false
    default: false
    type: bool
  failover_mode:
    description:  Determines the behavior when a Tier-0 instance in ACTIVE-STANDBY
                  high-availability mode restarts after a failure. If set to
                  PREEMPTIVE, the preferred node will take over, even if it causes
                  another failure. If set to NON_PREEMPTIVE, then the instance that
                  restarted will remain secondary. This property must not be populated
                  unless the ha_mode property is set to ACTIVE_STANDBY.
    required: false
    default: NON_PREEMPTIVE
    choices:
      - NON_PREEMPTIVE
      - PREEMPTIVE
    type: str
  ipv6_profile_paths:
    description:  IPv6 NDRA and DAD profiles configuration
                  IPv6 NDRA and DAD profiles configuration on tier1. Either or both
                  NDRA and/or DAD profiles can be configured.
                  Minimum items: 0
                  Maximum items: 2
    required: false
    default: ["/infra/ipv6-ndra-profiles/default", "/infra/ipv6-dad-profiles/default"]
    type: list
  tier0_path:
    description:  Specify Tier-1 connectivity to Tier-0 instance.
    type: str
    required: false
  type:
    description:  Tier1 connectivity type for reference. Property value is not validated
                  with Tier1 configuration.
                  ROUTED: Tier1 is connected to Tier0 gateway and routing is enabled.
                  ISOLATED: Tier1 is not connected to any Tier0 gateway.
                  NATTED: Tier1 is in ROUTED type with NAT configured locally.
    choices:
      - ROUTED
      - ISOLATED
      - NATTED
    default: ROUTED
    type: str
"""

EXAMPLES = """

nsxt_policy_tier1s:
  hostname: "nsxvip.domain.local"
  username: "admin"
  password: "Vmware1!"
  validate_certs: false
  display_name: "My_first_tier1s"
  description: "My first tier1s automated created by Ansible for NSX-T policy"
"""

RETURN = """# """


def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(
        display_name=dict(required=True, type="str"),
        state=dict(required=True, choices=["present", "absent"]),
        default_rule_logging=dict(required=False, type="bool", default=False),
        description=dict(required=False, type="str"),
        dhcp_config_paths=dict(required=False, type="list"),
        disable_firewall=dict(required=False, type="bool", default=False),
        enable_standby_relocation=dict(required=False, type="bool", default=False),
        failover_mode=dict(
            required=False,
            type="str",
            default="NON_PREEMPTIVE",
            choices=["NON_PREEMPTIVE", "PREEMPTIVE"],
        ),
        force_whitelisting=dict(required=False, type="bool", default=False),
        ipv6_profile_paths=dict(
            required=False,
            type="list",
            default=[
                "/infra/ipv6-ndra-profiles/default",
                "/infra/ipv6-dad-profiles/default",
            ],
        ),
        tier0_path=dict(required=False, type="str"),
        type=dict(
            required=False,
            type="str",
            choices=["ROUTED", "ISOLATED", "NATTED"],
            default="ROUTED",
        ),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    api_endpoint = "tier-1s"
    object_def = "tier-1"
    api_params_to_remove = ["resource_type"]

    api_protected_params = ["ha_mode", "transit_subnets", "internal_transit_subnets"]

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
