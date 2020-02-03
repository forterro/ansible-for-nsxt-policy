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
module: nsxt_policy_security_policies

short_description: Manage NSX-T security_policies with policy APIS

description: Manage NSX-T security_policies with policy APIS

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
    category:
        description:
            -  	"A way to classify a security policy, if needed."

            - "Distributed Firewall -
                Policy framework provides five pre-defined categories for classifying
                a security policy. They are "Ethernet","Emergency", "Infrastructure"
                "Environment" and "Application". There is a pre-determined order in
                which the policy framework manages the priority of these security
                policies. Ethernet category is for supporting layer 2 firewall rules.
                The other four categories are applicable for layer 3 rules. Amongst
                them, the Emergency category has the highest priority followed by
                Infrastructure, Environment and then Application rules. Administrator
                can choose to categorize a security policy into the above categories
                or can choose to leave it empty. If empty it will have the least
                precedence w.r.t the above four categories."
            - "Edge Firewall -
                Policy Framework for Edge Firewall provides six pre-defined categories
                "Emergency", "SystemRules", "SharedPreRules", "LocalGatewayRules",
                "AutoServiceRules" and "Default", in order of priority of rules.
                All categories are allowed for Gatetway Policies that belong
                to 'default' Domain. However, for user created domains, category is
                restricted to "SharedPreRules" or "LocalGatewayRules" only. Also, the
                users can add/modify/delete rules from only the "SharedPreRules" and
                "LocalGatewayRules" categories. If user doesn't specify the category
                then defaulted to "Rules". System generated category is used by NSX
                created rules, for example BFD rules. Autoplumbed category used by
                NSX verticals to autoplumb data path rules. Finally, "Default" category
                is the placeholder default rules with lowest in the order of priority."
        required: false
        type: str
    comments:
        description:
            - "SecurityPolicy lock/unlock comments"
        required: false
        type: str
    locked:
        description:
            -  "Indicates whether a security policy should be locked. If the
                security policy is locked by a user, then no other user would
                be able to modify this security policy. Once the user releases
                the lock, other users can update this security policy."
        required: false
        type: bool
        default: false
    rules:
        description:
            - "Rules that are a part of this SecurityPolicy"
        required: false
        type: list
        suboptions:
            action:
                description:
                   - "The action to be applied to all the services"
                required: true
                type: str
                choices:
                    - ALLOW
                    - DROP
                    - REJECT
            destination_groups:
                description:
                    - "Destination group paths"
                    -" We need paths as duplicate names may exist for groups under different
                        domains.In order to specify all groups, use the constant "ANY". This
                        is case insensitive. If "ANY" is used, it should be the ONLY element
                        in the group array. Error will be thrown if ANY is used in conjunction
                        with other values."
                required: false
                type: list
                elements: str
            destinations_excluded:
                description:
                    - "If set to true, the rule gets applied on all the groups that are
                        NOT part of the destination groups. If false, the rule applies to the
                        destination groups"
                    required: false
                    type: boolean
                    default: false
            direction:
                description: "Define direction of traffic."
                required: false
                type: str
                choices:
                   - IN
                   - OUT
                   - IN_OUT
                default: IN_OUT
            disabled:
                description: "Flag to disable the rule. Default is enabled."
                required: false
                type: boolean
                default: false
            ip_protocol:
                description:
                    - "Type of IP packet that should be matched while enforcing the rule.
                        The value is set to IPV4_IPV6 for Layer3 rule if not specified.
                        For Layer2/Ether rule the value must be null."
                required: false
                type: str
                choices:
                   - IPV4
                   - IPV6
                   - IPV4_IPV6
            logged:
                description: "Flag to enable packet logging. Default is disabled."
                required: false
                type: boolean
                default: false
            notes:
                description: "Text for additional notes on changes."
                required: false
                type: str
            profiles:
                description:
                    - "Layer 7 service profiles"
                    - "Holds the list of layer 7 service profile paths. These profiles accept
                        attributes and sub-attributes of various network services
                        (e.g. L4 AppId, encryption algorithm, domain name, etc) as key value
                        pairs."
                required: false
                type: list
                elements: str
            scope:
                description:
                    - "The list of policy paths where the rule is applied
                        LR/Edge/T0/T1/LRP etc. Note that a given rule can be applied
                        on multiple LRs/LRPs."
                required: false
                type: list
                elements: str
            sequence_number:
                description:
                    - "This field is used to resolve conflicts between multiple
                        Rules under Security or Gateway Policy for a Domain
                        If no sequence number is specified in the payload, a value of 0 is
                        assigned by default. If there are multiple rules with the same
                        sequence number then their order is not deterministic. If a specific
                        order of rules is desired, then one has to specify unique sequence
                        numbers or use the POST request on the rule entity with
                        a query parameter action=revise to let the framework assign a
                        sequence number"
                required: false
                type: int
            services:
                description:
                    - "In order to specify all services, use the constant "ANY".
                        This is case insensitive. If "ANY" is used, it should
                        be the ONLY element in the services array. Error will be thrown
                        if ANY is used in conjunction with other values."
                required: false
                type: list
                elements: str
            source_groups:
                description:
                    - "We need paths as duplicate names may exist for groups under different
                        domains. In order to specify all groups, use the constant "ANY". This
                        is case insensitive. If "ANY" is used, it should be the ONLY element
                        in the group array. Error will be thrown if ANY is used in conjunction
                        with other values."
                required: false
                type: list
                elements: str
            sources_excluded:
                description:
                    - "If set to true, the rule gets applied on all the groups that are
                        NOT part of the source groups. If false, the rule applies to the
                        source groups"
                required: false
                type: boolean
                default: false
    scope:
        description:
            - "The list of group paths where the rules in this policy will get
                applied. This scope will take precedence over rule level scope.
                Supported only for security policies."
        required: false
        type: list
        elements: str
    stateful:
        description:
            - "Stateful or Stateless nature of security policy is enforced on all
                rules in this security policy. When it is stateful, the state of
                the network connects are tracked and a stateful packet inspection is
                performed.
                Layer3 security policies can be stateful or stateless. By default, they are stateful.
                Layer2 security policies can only be stateless."
        required: false
        type: boolean
    tcp_strict:
        description:
            - "Enforce strict tcp handshake before allowing data packets
                Ensures that a 3 way TCP handshake is done before the data packets
                are sent.
                tcp_strict=true is supported only for stateful security policies."
        required: false
        type: boolean



"""

EXAMPLES = """
nsxt_policy_security_policies:
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    display_name: "My_first_security_policy"
    description: "My first security_policies automated created by Ansible for NSX-T policy"
    category: "Application"
    rules:
        - description: " comm entry"
          display_name: "ce-1"
          sequence_number: 1
          source_groups:
            - "/infra/domains/vmc/groups/dbgroup"
          destination_groups:
            - "/infra/domains/vmc/groups/appgroup"
          services:
            - "/infra/services/HTTP"
            - "/infra/services/CIM-HTTP"
          action: "ALLOW"
"""

RETURN = """# """


def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(
        display_name=dict(required=True, type="str"),
        description=dict(required=False, type="str"),
        state=dict(required=True, choices=["present", "absent"]),
        domain=dict(required=False, type="str", default="default"),
        tags=dict(required=False, type="list"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    api_endpoint = "security-policies"  # Define API endpoint for object (eg: segments)
    object_def = "security-policy"  # Define object name (eg: segment)

    # Define api params to remove from returned object to get same object as ansible object
    api_params_to_remove = ["resource_type"]

    # Define read only params to fail module if call try to update
    api_protected_params = []

    # Define params from ansible to remove for correct object as nsx api object
    ansible_params_to_remove = ["domain"]

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
