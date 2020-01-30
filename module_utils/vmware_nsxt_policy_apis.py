#!/usr/bin/env python
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

import json, time, requests, urllib3
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from requests.auth import HTTPBasicAuth
from deepdiff import DeepDiff
from pprint import pprint


def vmware_argument_spec():
    return dict(
        hostname=dict(type="str", required=True),
        username=dict(type="str", required=True),
        password=dict(type="str", required=True, no_log=True),
        port=dict(type="int", default=443),
        validate_certs=dict(type="bool", required=False, default=True),
    )


def request(
    url,
    data=None,
    headers=None,
    method="GET",
    use_proxy=True,
    force=False,
    last_mod_time=None,
    timeout=300,
    validate_certs=True,
    url_username=None,
    url_password=None,
    http_agent=None,
    force_basic_auth=True,
    ignore_errors=False,
    port=443,
):
    try:
        requests.packages.urllib3.disable_warnings()
        s = requests.session()
        s.auth = HTTPBasicAuth(url_username, url_password)
        s.verify = validate_certs
        s.headers.update(headers)
        if method == "GET":
            r = s.get(url)
        elif method == "PATCH":
            r = s.patch(url, data=data)
        elif method == "POST":
            r = s.post(url, data=data)
        elif method == "PUT":
            r = s.post(url, data=data)
        elif method == "DELETE":
            r = s.delete(url)
    except Exception as err:
        print(err)
        r = err.fp

    try:
        raw_data = r.content
        if raw_data:
            data = json.loads(raw_data)
        else:
            raw_data = None
    except:
        if ignore_errors:
            pass
        else:
            raise Exception(raw_data)

    resp_code = r.status_code

    if resp_code >= 400 and not ignore_errors:
        raise Exception(resp_code, data)
    if not (data is None) and data.__contains__("error_code"):
        raise Exception(data["error_code"], data)
    else:
        return resp_code, data


# def order_dict(dictionary):
#     result = {}
#     for k, v in sorted(dictionary.items()):
#         if isinstance(v, dict):
#             result[k] = order_dict(v)
#         elif isinstance(v, list):
#             for e in v:
#                 if isinstance(e, dict):
#                     for sk, sv in sorted(e.items()):
#                         if isinstance(sv, dict):
#                             result[sk] = order_dict(sv)
#                         elif isinstance(sv, list):
#                             sv.sort()
#                         else:
#                             result[sk] = sv
#                 elif isinstance(e, list):
#                     result[k] = sorted(e)
#                 else:
#                     result[k] = e
#         else:
#             result[k] = v
#     return result


def sort_key_func(item):
    """ helper function used to sort list of dicts

    :param item: dict
    :return: sorted list of tuples (k, v)
    """
    pairs = []
    for k, v in item.items():
        pairs.append((k, v))
    return sorted(pairs)


def recurse_compare_dict(d1, d2, is_different=False):
    # Compare keys
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    d1_d2_key_diff = d1_keys ^ d2_keys
    if bool(d1_d2_key_diff):
        print("dict attributes are differents ! %s" % (d1_d2_key_diff))
        is_different = True
    # Compare recursively
    else:
        for k, v in sorted(d1.items()):
            if isinstance(v, dict):
                is_different = recurse_compare_dict(v, d2[k], is_different)
            elif isinstance(v, list):
                if len(v) != len(d2[k]):
                    print(
                        "list size differs, it's different ! d1 list : %s - d2 list : %s"
                        % (v, d2[k])
                    )
                    is_different = True
                else:
                    index = 0

                    if len(v) > 0 and isinstance(v[0], dict):
                        v_keys = set(v[0].keys())
                        ordered_v = sorted(
                            v,
                            key=lambda d: next(
                                (i for (i, y) in enumerate(v_keys) if y in d),
                                len(v_keys) + 1,
                            ),
                        )
                        ordered_d2 = sorted(
                            d2[k],
                            key=lambda d: next(
                                (i for (i, y) in enumerate(v_keys) if y in d),
                                len(v_keys) + 1,
                            ),
                        )
                        for e in ordered_v:
                            if isinstance(e, dict):
                                is_different = recurse_compare_dict(
                                    e, ordered_d2[index], is_different
                                )
                            else:
                                if str(e) != str(ordered_d2[index]):
                                    print(
                                        "value differs, it's different ! d1 value : %s - d2 value %s"
                                        % (e, ordered_d2[index])
                                    )
                                    is_different = True
                            index += 1
            else:
                if str(v) != str(d2[k]):
                    print(
                        "value differs, it's different ! d1 value : %s - d2 value %s"
                        % (v, d2[k])
                    )
                    is_different = True
    return is_different


# Remove vmware_nsxt module util parameters and return specific params for this nsx-t module
def get_nsx_module_params(args=None, args_to_remove=None):
    ansible_params_to_remove = [
        "state",
        "username",
        "password",
        "port",
        "hostname",
        "validate_certs",
        "display_name",
    ]
    args_to_remove += ansible_params_to_remove
    for key in args_to_remove:
        args.pop(key, None)
    for key, value in args.copy().items():
        if value == None:
            args.pop(key, None)
    return args


# Remove unecessary api params to have similar object between ansible and api
def remove_api_params(object, params_to_remove):
    int_object = object
    api_params_to_remove = [
        "_links",
        "_schema",
        "_self",
        "display_name",
        "type",
        "marked_for_delete",
        "id",
        "path",
        "parent_path",
        "relative_path",
        "_create_user",
        "_create_time",
        "_last_modified_user",
        "_last_modified_time",
        "_system_owned",
        "_protection",
        "_revision",
    ]
    params_to_remove += api_params_to_remove
    for key in params_to_remove:
        int_object.pop(key, None)
    for key, value in int_object.copy().items():
        if value == None:
            int_object.pop(key, None)
    return int_object


# Get all nsx-t objects for current api endpoint
def get_nsx_objects(
    module,
    manager_url,
    api_endpoint,
    mgr_username,
    mgr_password,
    validate_certs,
    object_def,
):
    try:
        headers = dict(Accept="application/json")
        headers["Content-Type"] = "application/json"
        (rc, resp) = request(
            url=manager_url + "/" + api_endpoint,
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
    return resp


# Get nsx-t object with display name
def get_nsx_object(
    module,
    manager_url,
    api_endpoint,
    mgr_username,
    mgr_password,
    validate_certs,
    display_name,
    object_def,
):
    objects = get_nsx_objects(
        module=module,
        manager_url=manager_url,
        api_endpoint=api_endpoint,
        mgr_username=mgr_username,
        mgr_password=mgr_password,
        validate_certs=validate_certs,
        object_def=object_def,
    )
    for object in objects["results"]:
        if (
            object.__contains__("display_name")
            and object["display_name"] == display_name
        ):
            return object
        elif object.__contains__("id") and object["id"] == display_name:
            return object
    return None


# Check if object must be updated
def check_for_update(module, object, params, params_to_remove, protected_params):
    clean_object = remove_api_params(object=object, params_to_remove=params_to_remove)

    print("Debug - object returned by api : %s" % (clean_object))
    print("Debug - object passed in params : %s" % (params))
    for key in protected_params:
        if (
            (clean_object.__contains__(key) and not params.__contains__(key))
            or (not clean_object.__contains__(key) and params.__contains__(key))
            or (
                clean_object.__contains__(key)
                and params.__contains__(key)
                and clean_object[key] != params[key]
            )
        ):
            module.fail_json(
                msg="Parameter %s is protected. You cannot update this attribute."
                % (key)
            )
    if bool(params) or bool(clean_object):
        result = recurse_compare_dict(params, clean_object)
    else:
        result = False
    return result


def create_or_update_nsx_object(
    module,
    manager_url,
    api_endpoint,
    mgr_username,
    mgr_password,
    validate_certs,
    params,
    display_name,
    object_def,
    update_method,
    post_action=None,
):
    if module.check_mode:
        module.exit_json(
            changed=True, debug_out=str(json.dumps(params)), id=display_name
        )

    try:
        headers = dict(Accept="application/json")
        headers["Content-Type"] = "application/json"

        request_data = json.dumps(params)
        if update_method == "PATCH":
            (rc, resp) = request(
                url=manager_url + "/" + api_endpoint + "/%s" % display_name,
                headers=headers,
                data=request_data,
                method="PATCH",
                url_username=mgr_username,
                url_password=mgr_password,
                validate_certs=validate_certs,
            )
        elif update_method == "POST":
            (rc, resp) = request(
                url=manager_url + "/" + api_endpoint + "?action=%s" % post_action,
                headers=headers,
                data=request_data,
                method="POST",
                url_username=mgr_username,
                url_password=mgr_password,
                validate_certs=validate_certs,
            )

    except Exception as err:
        module.fail_json(
            msg="Failed to create or update %s with name %s. Error[%s]."
            % (object_def, display_name, to_native(err))
        )

    time.sleep(5)

    module.exit_json(
        changed=True,
        object_name=display_name,
        message="%s with name %s created or updated." % (object_def, display_name),
    )


def delete_nsx_object(
    module,
    manager_url,
    api_endpoint,
    mgr_username,
    mgr_password,
    validate_certs,
    display_name,
    object_def,
):
    if module.check_mode:
        module.exit_json(changed=True, debug_out=str(id=display_name))
    try:
        headers = dict(Accept="application/json")
        headers["Content-Type"] = "application/json"
        (rc, resp) = request(
            url=manager_url + "/" + api_endpoint + "/%s" % display_name,
            method="DELETE",
            url_username=mgr_username,
            url_password=mgr_password,
            validate_certs=validate_certs,
            headers=headers,
        )
    except Exception as err:
        module.fail_json(
            msg="Failed to delete %s with name %s. Error[%s]."
            % (object_def, display_name, to_native(err))
        )

    time.sleep(5)
    module.exit_json(
        changed=True,
        object_name=display_name,
        message="%s with name %s deleted." % (object_def, display_name),
    )


def nsx_module_execution(
    module,
    manager_url,
    api_endpoint,
    object_def,
    api_params_to_remove,
    api_protected_params,
    ansible_params_to_remove,
    update_method="PATCH",
    post_action=None,
):

    nsx_module_params = get_nsx_module_params(
        module.params.copy(), ansible_params_to_remove
    )

    state = module.params["state"]
    mgr_hostname = module.params["hostname"]
    mgr_username = module.params["username"]
    mgr_password = module.params["password"]
    validate_certs = module.params["validate_certs"]
    display_name = module.params["display_name"]

    # Search for nsx object
    nsx_object = get_nsx_object(
        module=module,
        manager_url=manager_url,
        api_endpoint=api_endpoint,
        mgr_username=mgr_username,
        mgr_password=mgr_password,
        validate_certs=validate_certs,
        display_name=display_name,
        object_def=object_def,
    )

    if nsx_object:
        exits_object = True
    else:
        exits_object = False
    # Present state
    if state == "present":

        # If object already exists, check for update
        if exits_object:
            to_update = check_for_update(
                module=module,
                object=nsx_object,
                params=nsx_module_params,
                params_to_remove=api_params_to_remove,
                protected_params=api_protected_params,
            )

        # Create or update NSX object
        if not exits_object or to_update:
            create_or_update_nsx_object(
                module=module,
                manager_url=manager_url,
                api_endpoint=api_endpoint,
                mgr_username=mgr_username,
                mgr_password=mgr_password,
                validate_certs=validate_certs,
                params=nsx_module_params,
                display_name=display_name,
                object_def=object_def,
                update_method=update_method,
                post_action=post_action,
            )
        else:
            module.exit_json(
                changed=False,
                msg="%s with display name %s is up to date"
                % (object_def, display_name),
            )

    # Absent state
    if state == "absent":
        if nsx_object:
            delete_nsx_object(
                module=module,
                manager_url=manager_url,
                api_endpoint=api_endpoint,
                mgr_username=mgr_username,
                mgr_password=mgr_password,
                validate_certs=validate_certs,
                display_name=display_name,
                object_def=object_def,
            )
        else:
            module.exit_json(
                changed=False,
                msg="No %s exist with display name %s" % (object_def, display_name),
            )


def nsx_module_facts_execution(module, manager_url, api_endpoint, object_def):
    mgr_hostname = module.params["hostname"]
    mgr_username = module.params["username"]
    mgr_password = module.params["password"]
    validate_certs = module.params["validate_certs"]

    output = {}
    if module.params["display_name"]:
        display_name = module.params["display_name"]
        api_json = get_nsx_object(
            module=module,
            manager_url=manager_url,
            api_endpoint=api_endpoint,
            mgr_username=mgr_username,
            mgr_password=mgr_password,
            validate_certs=validate_certs,
            display_name=display_name,
            object_def=object_def,
        )
        output[object_def.replace("-", "_")] = api_json

    else:
        api_json = get_nsx_objects(
            module=module,
            manager_url=manager_url,
            api_endpoint=api_endpoint,
            mgr_username=mgr_username,
            mgr_password=mgr_password,
            validate_certs=validate_certs,
            object_def=object_def,
        )
        output[api_endpoint.replace("-", "_")] = api_json["results"]

    module.exit_json(changed=False, **output)
