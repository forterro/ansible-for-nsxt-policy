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
module: nsxt_policy_lb_virtual_servers
short_description: Manage NSX-T lb_virtual_servers  with policy APIS

description: Manage NSX-T lb_virtual_servers  with policy APIS

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
  access_log_enabled:
    desciption:
      - "If access log is enabled, all HTTP requests sent to an L7 virtual
        server are logged to the access log file. Both successful requests
        (backend server returns 2xx) and unsuccessful requests (backend
        server returns 4xx or 5xx) are logged to access log, if enabled."
    required: false
    type: boolean
    default: false
  application_profile_path:
    description:
      - "The application profile defines the application protocol characteristics.
        It is used to influence how load balancing is performed. Currently,
        LBFastTCPProfile, LBFastUDPProfile and
        LBHttpProfile, etc are supported."
    required: true
  client_ssl_profile_binding:
    description:
      - "The setting is used when load balancer acts as an SSL server and
        terminating the client SSL connection"
    required: false
    type: dict
    suboptions:
      certificate_chain_depth:
        description:
          - "Authentication depth is used to set the verification depth in the client certificates chain."
        type: int
        required: false
        default: 3
      client_auth:
        description:
          - "Client authentication mode."
        required: false
        type: str
        choices:
          - REQUIRED
          - IGNORE
        default: IGNORE
      client_auth_ca_paths:
        description:
          - "If client auth type is REQUIRED, client certificate must be signed by
            one of the trusted Certificate Authorities (CAs), also referred to as
            root CAs, whose self signed certificates are specified."
        required: false
        type: list
        elements: str
      client_auth_crl_paths:
        description:
          - "A Certificate Revocation List (CRL) can be specified in the client-side
            SSL profile binding to disallow compromised client certificates."
        required: false
        type: list
        elements: str
      default_certificate_path:
        description:
          - "A default certificate should be specified which will be used if the
            server does not host multiple hostnames on the same IP address or if
            the client does not support SNI extension."
        type: str
        required: true
      sni_certificate_paths:
        description:
          - "Client-side SSL profile binding allows multiple certificates, for
            different hostnames, to be bound to the same virtual server."
        required: false
        type: list
        elements: str
      ssl_profile_path:
        description:
          - "Client SSL profile defines reusable, application-independent client side SSL properties."
        required: false
        type: str
  default_pool_member_ports:
    description:
      - "Default pool member ports when member port is not defined."
      - "A port or a port range"
      - "Examples- Single port '8080', Range of ports '8090-8095'"
      - "Maximum items : 14"
    required: false
    type: list
    elements: str
  enabled:
    description:
      - "Flag to enable the load balancer virtual server."
    required: false
    type: boolean
    default: true
  ip_address:
    description:
      - "Configures the IP address of the LBVirtualServer where it
        receives all client connections and distributes them among the
        backend servers."
    required: true
    type: str
  lb_persistence_profile_path:
    description:
      - "Path to optional object that enables persistence on a virtual server
        allowing related client connections to be sent to the same backend
        server. Persistence is disabled by default."
    required: false
    type: str
  lb_service_path:
    description:
      - "virtual servers can be associated to LBService(which is
        similar to physical/virtual load balancer), LB virtual servers,
        pools and other entities could be defined independently, the LBService
        identifier list here would be used to maintain the relationship of
        LBService and other LB entities."
    required: false
    type: str
  max_concurrent_connections:
    description:
      - "To ensure one virtual server does not over consume resources,
        affecting other applications hosted on the same LBS, connections
        to a virtual server can be capped.
        If it is not specified, it means that connections are unlimited."
    required: false
    type: int
  max_new_connection_rate:
    description:
      - "To ensure one virtual server does not over consume resources,
        connections to a member can be rate limited.
        If it is not specified, it means that connection rate is unlimited."
    required: false
    type: int
  pool_path:
    description:
      - "Default server pool path"
      - "The server pool(LBPool) contains backend servers. Server pool
        consists of one or more servers, also referred to as pool members, that
        are similarly configured and are running the same application."
    required: false
    type: str
  ports:
    description:
      - "Virtual server port number(s) or port range(s)
      - "Ports contains a list of at least one port or port range such as '80',
        '1234-1236'. Each port element in the list should be a single port or a
        single port range."
    required: true
    type: str
  rules:
    description:
      - "Load balancer rules allow customization of load balancing behavior using
        match/action rules. Currently, load balancer rules are supported for
        only layer 7 virtual servers with LBHttpProfile."
      - "doc : https://vdc-download.vmware.com/vmwb-repository/dcr-public/ec5a04ad-00be-4362-9092-7e934609879b/0c127b7e-6d1f-4730-a6db-5f52cba4daf5/api_includes/types_LBRule.html"
    required: false
    type: list
    elements: str
  server_ssl_profile_binding:
    description:
      - "The setting is used when load balancer acts as an SSL client and
        establishing a connection to the backend server."
      - "doc : https://vdc-download.vmware.com/vmwb-repository/dcr-public/ec5a04ad-00be-4362-9092-7e934609879b/0c127b7e-6d1f-4730-a6db-5f52cba4daf5/api_includes/types_LBServerSslProfileBinding.html"
    requied: false
  sorry_pool_path:
    description:
      - "When load balancer can not select a backend server to serve the
        request in default pool or pool in rules, the request would be served
        by sorry server pool."
    required: false
    type: str


"""

EXAMPLES = """
nsxt_policy_lb_virtual_servers
    hostname: "nsxvip.domain.local"
    username: "admin"
    password: "Vmware1!"
    validate_certs: false
    display_name: "My_first_lb_virtual_server"
    description: "My first lb_virtual_servers automated created by Ansible for NSX-T policy"
    ip_address: "30.1.1.1"
    ports:
      - "1019"
    application_profile_path: "/infra/lb-app-profiles/default-tcp-lb-app-profile"
"""

RETURN = """# """


def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(
        display_name=dict(required=True, type="str"),
        description=dict(required=False, type="str"),
        state=dict(required=True, choices=["present", "absent"]),
        access_log_enabled=dict(required=False, type="bool", default=False),
        application_profile_path=dict(required=True, type="str"),
        client_ssl_profile_binding=dict(required=False, type="dict"),
        default_pool_member_ports=dict(required=False, type="list"),
        enabled=dict(required=False, type="bool", default=True),
        ip_address=dict(required=True, type="str"),
        lb_persistence_profile_path=dict(required=False, type="str"),
        lb_service_path=dict(required=False, type="str"),
        max_concurrent_connections=dict(required=False, type="int"),
        max_new_connection_rate=dict(required=False, type="int"),
        pool_path=dict(required=False, type="str"),
        ports=dict(required=True, type="list"),
        rules=dict(required=False, type="str"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    api_endpoint = "lb-virtual-servers"  # Define API endpoint for object (eg: segments)
    object_def = "lb-virtual-server"  # Define object name (eg: segment)

    # Define api params to remove from returned object to get same object as ansible object
    api_params_to_remove = []

    # Define read only params to fail module if call try to update
    api_protected_params = []

    # Define params from ansible to remove for correct object as nsx api object
    ansible_params_to_remove = []

    manager_url = "https://{}/policy/api/v1/infra".format(module.params["hostname"])

    module.params["resource_type"] = "LBVirtualServer"

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
