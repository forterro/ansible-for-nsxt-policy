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
module: nsxt_policy_lb_pools
short_description: Manage NSX-T lb_pools  with policy APIS

description: Manage NSX-T lb_pools  with policy APIS

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
  active_monitor_paths:
    description:
      - "In case of active healthchecks, load balancer itself initiates new connections (or sends ICMP ping) to the servers periodically to check their health,
         completely independent of any data traffic. Active healthchecks are disabled by default and can be enabled for a server pool by binding a health
         monitor to the pool. Currently, only one active health monitor can be configured per server pool."
      -  	Maximum items: 1
    type: list:
    elements: str
  algorithm:
    description:
      - "Load Balancing algorithm chooses a server for each new connection by going
          through the list of servers in the pool. Currently, following load balancing
          algorithms are supported with ROUND_ROBIN as the default."
      - "ROUND_ROBIN means that a server is selected in a round-robin fashion. The
        weight would be ignored even if it is configured."
      - "WEIGHTED_ROUND_ROBIN means that a server is selected in a weighted
        round-robin fashion. Default weight of 1 is used if weight is not configured."
      - "LEAST_CONNECTION means that a server is selected when it has the least
        number of connections. The weight would be ignored even if it is configured.
        Slow start would be enabled by default."
      - "WEIGHTED_LEAST_CONNECTION means that a server is selected in a weighted
        least connection fashion. Default weight of 1 is used if weight is not
        configured. Slow start would be enabled by default."
      - "IP_HASH means that consistent hash is performed on the source IP address of
        the incoming connection. This ensures that the same client IP address will
        always reach the same server as long as no server goes down or up. It may
        be used on the Internet to provide a best-effort stickiness to clients
        which refuse session cookies."
    default: "ROUND_ROBIN"
    choices:
      - ROUND_ROBIN
      - WEIGHTED_ROUND_ROBIN
      - LEAST_CONNECTION
      - WEIGHTED_LEAST_CONNECTION
      - IP_HASH
    type: str
  member_group:
    description:
      - "Load balancer pool support grouping object as dynamic pool members."
      - "When member group is defined, members setting should not be specified."
    type: dict
    required: false
    suboptions:
      group_path:
        description:
          - "Load balancer pool support Group as dynamic pool members."
          - "The IP list of the Group would be used as pool member IP setting."
        type: str
        required: true
      ip_revision_filter:
        description:
          - "Ip revision filter is used to filter IPv4 or IPv6 addresses from the
              grouping object."
          - "If the filter is not specified, both IPv4 and IPv6 addresses would be
              used as server IPs."
          - "The link local and loopback addresses would be always filtered out."
        type: str
        requied: false
        choices:
          - IPV4
          - IPV6
          - IPV4_IPV6
        default: "IPV4"
      max_ip_list_size:
        description:
          - "The size is used to define the maximum number of grouping object IP
              address list. These IP addresses would be used as pool members.
              If the grouping object includes more than certain number of
              IP addresses, the redundant parts would be ignored and those IP
              addresses would not be treated as pool members.
              If the size is not specified, one member is budgeted for this dynamic
              pool so that the pool has at least one member even if some other
              dynamic pools grow beyond the capacity of load balancer service. Other
              members are picked according to available dynamic capacity. The unused
              members would be set to DISABLED so that the load balancer system
              itself is not overloaded during runtime."
        type: int
        required: false
      port:
        description:
          - "If port is specified, all connections will be sent to this port.
              If unset, the same port the client connected to will be used, it could
              be overridden by default_pool_member_ports setting in virtual server.
              The port should not specified for multiple ports case."
        type: int
        required: false
  members:
    description:
      - "Server pool consists of one or more pool members. Each pool member
         is identified, typically, by an IP address and a port."
    type: list
    required: false
    suboptions:
      admin_state:
        description:
          - "Member admin state"
        type: str
        default: "ENABLED"
        choices:
          - ENABLED
          - DISABLED
          - GRACEFUL_DISABLED
        required: false
      backup_member:
        description:
          - "Backup servers are typically configured with a sorry page indicating to
            the user that the application is currently unavailable. While the pool
            is active (a specified minimum number of pool members are active)
            BACKUP members are skipped during server selection. When the pool is
            inactive, incoming connections are sent to only the BACKUP member(s)."
        type: boolean
        default: false
        required: false
      display_name:
        description:
          - "Pool member name."
        required: false
        type: str
      ip_address:
        description:
          - "Pool member IP address."
        required: true
        type: str
      max_concurrent_connections:
        description:
          - "To ensure members are not overloaded, connections to a member can be
              capped by the load balancer. When a member reaches this limit, it is
              skipped during server selection.
              If it is not specified, it means that connections are unlimited."
        type: int
        required: false
      port:
        description:
          - "If port is specified, all connections will be sent to this port. Only
            single port is supported.
            If unset, the same port the client connected to will be used, it could
            be overrode by default_pool_member_port setting in virtual server.
            The port should not specified for port range case."
        required: false
        type: str
      weight:
        description:
          - "Pool member weight is used for WEIGHTED_ROUND_ROBIN balancing
            algorithm. The weight value would be ignored in other algorithms."
        type: int
        default: 1
        required: false
  min_active_members:
    description:
      - "Minimum number of active pool members to consider pool as active"
      - "A pool is considered active if there are at least certain minimum number of members."
    required: false
    type: int
    default: 1
  passive_monitor_path:
    description:
      - "Passive healthchecks are disabled by default and can be enabled by
        attaching a passive health monitor to a server pool.
        Each time a client connection to a pool member fails, its failed count
        is incremented. For pools bound to L7 virtual servers, a connection is
        considered to be failed and failed count is incremented if any TCP
        connection errors (e.g. TCP RST or failure to send data) or SSL
        handshake failures occur. For pools bound to L4 virtual servers, if no
        response is received to a TCP SYN sent to the pool member or if a TCP
        RST is received in response to a TCP SYN, then the pool member is
        considered to have failed and the failed count is incremented."
    type: str
    required: false
  snat_translation:
    description:
      - "Depending on the topology, Source NAT (SNAT) may be required to ensure
        traffic from the server destined to the client is received by the load
        balancer. SNAT can be enabled per pool. If SNAT is not enabled for a
        pool, then load balancer uses the client IP and port (spoofing) while
        establishing connections to the servers. This is referred to as no-SNAT
        or TRANSPARENT mode. By default Source NAT is enabled as LBSnatAutoMap."
    type: dict
    required: false
    suboptions:
      type:
        description: "type name"
        required: true
        type: str
        choices:
          - LBSnatAutoMap
          - LBSnatDisabled
          - LBSnatIpPool
        default: "LBSnatAutoMap"
  tcp_multiplexing_enabled:
    description:
      - "TCP multiplexing allows the same TCP connection between load balancer
        and the backend server to be used for sending multiple client requests
        from different client TCP connections."
    type: boolean
    required: false
    default: false
  tcp_multiplexing_number:
    description:
      - "The maximum number of TCP connections per pool that are idly kept alive
        for sending future client requests."
    type: int
    default: 6
    required: false
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
nsxt_policy_lb_pools
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    display_name: "My_first_ippool"
    description: "My first lb_pools automated created by Ansible for NSX-T policy"
    active_monitor_paths:
      - /infra/lb-monitor-profiles/default-http-lb-monitor
    snat_translation:
      type: LBSnatAutoMap
    member_group:
      group_path: /infra/domains/testDom/groups/testGroup
      port: 80
"""

RETURN = """# """


def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(
        display_name=dict(required=True, type="str"),
        description=dict(required=False, type="str"),
        state=dict(required=True, choices=["present", "absent"]),
        active_monitor_paths=dict(required=False, type="list"),
        algorithm=dict(required=False, type="str", default="ROUND_ROBIN"),
        member_group=dict(required=False, type="dict"),
        members=dict(required=False, type="list"),
        min_active_members=dict(required=False, type="int", default=1),
        passive_monitor_path=dict(required=False, type="str"),
        snat_translation=dict(required=False, type="dict"),
        tcp_multiplexing_enabled=dict(required=False, type="bool", default=False),
        tcp_multiplexing_number=dict(required=False, type="int", default=6),
        tags=dict(required=False, type="list"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    api_endpoint = "lb-pools"  # Define API endpoint for object (eg: segments)
    object_def = "lb-pool"  # Define object name (eg: segment)

    # Define api params to remove from returned object to get same object as ansible object
    api_params_to_remove = ["resource_type"]

    # Define read only params to fail module if call try to update
    api_protected_params = []

    # Define params from ansible to remove for correct object as nsx api object
    ansible_params_to_remove = []

    manager_url = "https://{}/policy/api/v1/infra".format(module.params["hostname"])

    if not bool(module.params["snat_translation"]):
        module.params["snat_translation"] = {}
        module.params["snat_translation"]["type"] = "LBSnatAutoMap"

    if bool(module.params["member_group"]):
        if not "ip_revision_filter" in module.params["member_group"]:
            module.params["member_group"]["ip_revision_filter"] = "IPV4"

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
