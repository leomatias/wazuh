# Copyright (C) 2015-2020, Wazuh Inc.
# Created by Wazuh, Inc. <info@wazuh.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

import logging
import re

from aiohttp import web

from api.authentication import generate_token
from api.configuration import default_security_configuration
from api.encoder import dumps, prettify
from api.models.base_model_ import Body
from api.models.configuration import SecurityConfigurationModel
from api.models.security import CreateUserModel, UpdateUserModel, RoleModel, PolicyModel
from api.models.token_response import TokenResponseModel
from api.util import remove_nones_to_dict, raise_if_exc, parse_api_param
from wazuh import security
from wazuh.core.cluster.control import get_system_nodes
from wazuh.core.cluster.dapi.dapi import DistributedAPI
from wazuh.core.exception import WazuhPermissionError, WazuhException
from wazuh.core.security import revoke_tokens
from wazuh.core.results import AffectedItemsWazuhResult
from wazuh.rbac import preprocessor

logger = logging.getLogger('wazuh')
auth_re = re.compile(r'basic (.*)', re.IGNORECASE)


async def login_user(request, user: str, auth_context=None):
    """User/password authentication to get an access token.
    This method should be called to get an API token. This token will expire at some time. # noqa: E501

    Parameters
    ----------
    request : connexion.request
    user : str
        Name of the user who wants to be authenticated
    auth_context : dict, optional
        User's authorization context

    Returns
    -------
    TokenResponseModel
    """
    f_kwargs = {'auth_context': auth_context,
                'user_id': user}

    dapi = DistributedAPI(f=preprocessor.get_permissions,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          logger=logger
                          )
    data = raise_if_exc(await dapi.distribute_function())

    try:
        token = generate_token(user_id=user, rbac_policies=data.dikt)
    except WazuhException as e:
        raise_if_exc(e)

    return web.json_response(data=TokenResponseModel(token=token), status=200, dumps=dumps)


async def get_user_me(request, pretty=False, wait_for_complete=False):
    """Returns information from all system roles.

    Parameters
    ----------
    request : connexion.request
    pretty : bool, optional
        Show results in human-readable format
    wait_for_complete : bool, optional
        Disable timeout response

    Returns
    -------
    Users information
    """
    dapi = DistributedAPI(f=security.get_user_me,
                          request_type='local_master',
                          is_async=False,
                          logger=logger,
                          wait_for_complete=wait_for_complete,
                          current_user=request['token_info']['sub'],
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def logout_user(request):
    """Invalidate all current user's tokens.

    Returns
    -------
    Status
    """

    dapi = DistributedAPI(f=security.revoke_current_user_tokens,
                          request_type='local_master',
                          is_async=False,
                          current_user=request['token_info']['sub'],
                          logger=logger
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=dumps)


async def get_users(request, user_ids: list = None, pretty=False, wait_for_complete=False,
                    offset=0, limit=None, search=None, sort=None):
    """Returns information from all system roles.

    Parameters
    ----------
    request : connexion.request
    user_ids : list, optional
        List of users to be obtained
    pretty : bool, optional
        Show results in human-readable format
    wait_for_complete : bool, optional
        Disable timeout response
    offset : int, optional
        First item to return
    limit : int, optional
        Maximum number of items to return
    search : str
        Looks for elements with the specified string
    sort : str, optional
        Sorts the collection by a field or fields (separated by comma). Use +/- at the beginning to list in
        ascending or descending order

    Returns
    -------
    Users information
    """
    f_kwargs = {'user_ids': user_ids, 'offset': offset, 'limit': limit,
                'sort_by': parse_api_param(sort, 'sort')['fields'] if sort is not None else ['id'],
                'sort_ascending': True if sort is None or parse_api_param(sort, 'sort')['order'] == 'asc' else False,
                'search_text': parse_api_param(search, 'search')['value'] if search is not None else None,
                'complementary_search': parse_api_param(search, 'search')['negation'] if search is not None else None}

    dapi = DistributedAPI(f=security.get_users,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          logger=logger,
                          wait_for_complete=wait_for_complete,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def create_user(request):
    """Create a new user.

    Parameters
    ----------
    request : connexion.request

    Returns
    -------
    User data
    """
    Body.validate_content_type(request, expected_content_type='application/json')
    f_kwargs = await CreateUserModel.get_kwargs(request)

    dapi = DistributedAPI(f=security.create_user,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=dumps)


async def update_user(request, user_id: str):
    """Modify an existent user.

    Parameters
    ----------
    request : connexion.request
    user_id : str
        User ID of the user to be updated

    Returns
    -------
    User data
    """
    Body.validate_content_type(request, expected_content_type='application/json')
    f_kwargs = await UpdateUserModel.get_kwargs(request, additional_kwargs={'user_id': user_id})

    dapi = DistributedAPI(f=security.update_user,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=dumps)


async def delete_users(request, user_ids: list = None):
    """Delete an existent list of users.

    Parameters
    ----------
    request : connexion.request
    user_ids : list, optional
        IDs of the users to be removed

    Returns
    -------
    Result of the operation
    """
    if 'all' in user_ids:
        user_ids = None
    f_kwargs = {'user_ids': user_ids}

    dapi = DistributedAPI(f=security.remove_users,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          logger=logger,
                          current_user=request['token_info']['sub'],
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=dumps)


async def get_roles(request, role_ids: list = None, pretty: bool = False, wait_for_complete: bool = False,
                    offset: int = 0, limit: int = None, search: str = None, sort: str = None):
    """

    Parameters
    ----------
    request : connexion.request
    role_ids : list, optional
        List of roles ids to be obtained
    pretty : bool, optional
        Show results in human-readable format
    wait_for_complete : bool, optional
        Disable timeout response
    offset : int, optional
        First item to return
    limit : int, optional
        Maximum number of items to return
    search : str, optional
        Looks for elements with the specified string
    sort : str, optional
        Sorts the collection by a field or fields (separated by comma). Use +/- at the beginning to list in
        ascending or descending order

    Returns
    -------
    Roles information
    """
    f_kwargs = {'role_ids': role_ids, 'offset': offset, 'limit': limit,
                'sort_by': parse_api_param(sort, 'sort')['fields'] if sort is not None else ['id'],
                'sort_ascending': True if sort is None or parse_api_param(sort, 'sort')['order'] == 'asc' else False,
                'search_text': parse_api_param(search, 'search')['value'] if search is not None else None,
                'complementary_search': parse_api_param(search, 'search')['negation'] if search is not None else None
                }

    dapi = DistributedAPI(f=security.get_roles,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          wait_for_complete=wait_for_complete,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def add_role(request, pretty: bool = False, wait_for_complete: bool = False):
    """Add one specified role.

    Parameters
    ----------
    request : request.connexion
    pretty : bool, optional
        Show results in human-readable format
    wait_for_complete : bool, optional
        Disable timeout response

    Returns
    -------
    Role information
    """
    # Get body parameters
    Body.validate_content_type(request, expected_content_type='application/json')
    f_kwargs = await RoleModel.get_kwargs(request)

    dapi = DistributedAPI(f=security.add_role,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          wait_for_complete=wait_for_complete,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def remove_roles(request, role_ids: list = None, pretty: bool = False, wait_for_complete: bool = False):
    """Removes a list of roles in the system.

    Parameters
    ----------
    request : connexion.request
    role_ids : list, optional
        List of roles ids to be deleted
    pretty : bool, optional
        Show results in human-readable format
    wait_for_complete : bool, optional
        Disable timeout response

    Returns
    -------
    Two list with deleted roles and not deleted roles
    """
    if 'all' in role_ids:
        role_ids = None
    f_kwargs = {'role_ids': role_ids}

    dapi = DistributedAPI(f=security.remove_roles,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          wait_for_complete=wait_for_complete,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def update_role(request, role_id: int, pretty: bool = False, wait_for_complete: bool = False):
    """Update the information of one specified role.

    Parameters
    ----------
    request : connexion.request
    role_id : int
        Specific role id in the system to be updated
    pretty : bool, optional
        Show results in human-readable format
    wait_for_complete : bool, optional
        Disable timeout response

    Returns
    -------
    Role information updated
    """
    # Get body parameters
    Body.validate_content_type(request, expected_content_type='application/json')
    f_kwargs = await RoleModel.get_kwargs(request, additional_kwargs={'role_id': role_id})

    dapi = DistributedAPI(f=security.update_role,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          wait_for_complete=wait_for_complete,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def get_policies(request, policy_ids: list = None, pretty: bool = False, wait_for_complete: bool = False,
                       offset: int = 0, limit: int = None, search: str = None, sort: str = None):
    """Returns information from all system policies.

    Parameters
    ----------
    request : connexion.request
    policy_ids : list, optional
        List of policies
    pretty : bool, optional
        Show results in human-readable format
    wait_for_complete : bool, optional
        Disable timeout response
    offset : int, optional
        First item to return
    limit : int, optional
        Maximum number of items to return
    search : str, optional
        Looks for elements with the specified string
    sort : str, optional
        Sorts the collection by a field or fields (separated by comma). Use +/- at the beginning to list in
        ascending or descending order

    Returns
    -------
    Policies information
    """
    f_kwargs = {'policy_ids': policy_ids, 'offset': offset, 'limit': limit,
                'sort_by': parse_api_param(sort, 'sort')['fields'] if sort is not None else ['id'],
                'sort_ascending': True if sort is None or parse_api_param(sort, 'sort')['order'] == 'asc' else False,
                'search_text': parse_api_param(search, 'search')['value'] if search is not None else None,
                'complementary_search': parse_api_param(search, 'search')['negation'] if search is not None else None
                }

    dapi = DistributedAPI(f=security.get_policies,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          wait_for_complete=wait_for_complete,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def add_policy(request, pretty: bool = False, wait_for_complete: bool = False):
    """Add one specified policy.

    Parameters
    ----------
    request : connexion.request
    pretty : bool, optional
        Show results in human-readable format
    wait_for_complete : bool, optional
        Disable timeout response

    Returns
    -------
    Policy information
    """
    # Get body parameters
    Body.validate_content_type(request, expected_content_type='application/json')
    f_kwargs = await PolicyModel.get_kwargs(request)

    dapi = DistributedAPI(f=security.add_policy,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          wait_for_complete=wait_for_complete,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def remove_policies(request, policy_ids: list = None, pretty: bool = False, wait_for_complete: bool = False):
    """Removes a list of roles in the system.

    Parameters
    ----------
    request : connexion.request
    policy_ids : list, optional
        List of policies ids to be deleted
    pretty : bool, optional
        Show results in human-readable format
    wait_for_complete : bool, optional
        Disable timeout response

    Returns
    -------
    Two list with deleted roles and not deleted roles
    """
    if 'all' in policy_ids:
        policy_ids = None
    f_kwargs = {'policy_ids': policy_ids}

    dapi = DistributedAPI(f=security.remove_policies,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          wait_for_complete=wait_for_complete,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def update_policy(request, policy_id: int, pretty: bool = False, wait_for_complete: bool = False):
    """Update the information of one specified policy.

    Parameters
    ----------
    request : connexion.request
    policy_id : int
        Specific policy id in the system to be updated
    pretty : bool, optional
        Show results in human-readable format
    wait_for_complete : bool, optional
        Disable timeout response

    Returns
    -------
    Policy information updated
    """
    # Get body parameters
    Body.validate_content_type(request, expected_content_type='application/json')
    f_kwargs = await PolicyModel.get_kwargs(request, additional_kwargs={'policy_id': policy_id})

    dapi = DistributedAPI(f=security.update_policy,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          wait_for_complete=wait_for_complete,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def set_user_role(request, user_id: str, role_ids: list, position: int = None,
                        pretty: bool = False, wait_for_complete: bool = False):
    """Add a list of roles to one specified user.

    Parameters
    ----------
    request : connexion.request
    user_id : str
        User ID
    role_ids : list of int
        List of role ids
    position : int, optional
        Position where the new role will be inserted
    pretty : bool, optional
        Show results in human-readable format
    wait_for_complete : bool, optional
        Disable timeout response

    Returns
    -------
    Dict
        User-Role information
    """
    f_kwargs = {'user_id': user_id, 'role_ids': role_ids, 'position': position}
    dapi = DistributedAPI(f=security.set_user_role,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          wait_for_complete=wait_for_complete,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def remove_user_role(request, user_id: str, role_ids: list, pretty: bool = False,
                           wait_for_complete: bool = False):
    """Delete a list of roles of one specified user.

    Parameters
    ----------
    request : connexion.request
    user_id : str
        User ID
    role_ids : list
        List of roles ids
    pretty : bool, optional
        Show results in human-readable format
    wait_for_complete: bool, optional
        Disable timeout response

    Returns
    -------
    Result of the operation
    """
    if 'all' in role_ids:
        role_ids = None
    f_kwargs = {'user_id': user_id, 'role_ids': role_ids}

    dapi = DistributedAPI(f=security.remove_user_role,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          wait_for_complete=wait_for_complete,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def set_role_policy(request, role_id, policy_ids, position=None, pretty=False, wait_for_complete=False):
    """Add a list of policies to one specified role.

    Parameters
    ----------
    role_id : int
        Role ID
    policy_ids : list of int
        List of policy IDs
    position : int
        Position where the new role will be inserted
    pretty : bool
        Show results in human-readable format
    wait_for_complete : bool
        Disable timeout response

    Returns
    -------
    dict
        Role information
    """
    f_kwargs = {'role_id': role_id, 'policy_ids': policy_ids, 'position': position}

    dapi = DistributedAPI(f=security.set_role_policy,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          wait_for_complete=wait_for_complete,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def remove_role_policy(request, role_id: int, policy_ids: list, pretty: bool = False,
                             wait_for_complete: bool = False):
    """Delete a list of policies of one specified role.

    Parameters
    ----------
    request : request.connexion
    role_id : int
    policy_ids : list
        List of policy ids
    pretty : bool, optional
        Show results in human-readable format
    wait_for_complete : bool, optional
        Disable timeout response

    Returns
    -------
    Role information
    """
    if 'all' in policy_ids:
        policy_ids = None
    f_kwargs = {'role_id': role_id, 'policy_ids': policy_ids}

    dapi = DistributedAPI(f=security.remove_role_policy,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          wait_for_complete=wait_for_complete,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def get_rbac_resources(pretty: bool = False, resource: str = None):
    """Gets all the current defined resources for RBAC.

    Parameters
    ----------
    pretty : bool, optional
        Show results in human-readable format
    resource : str, optional
        Show the information of the specified resource. Ex: agent:id

    Returns
    -------
    dict
        RBAC resources
    """
    f_kwargs = {'resource': resource}

    dapi = DistributedAPI(f=security.get_rbac_resources,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_any',
                          is_async=False,
                          wait_for_complete=True,
                          logger=logger
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def get_rbac_actions(pretty: bool = False, endpoint: str = None):
    """Gets all the current defined actions for RBAC.

    Parameters
    ----------
    pretty : bool, optional
        Show results in human-readable format
    endpoint : str, optional
        Show actions and resources for the specified endpoint. Ex: GET /agents

    Returns
    -------
    dict
        RBAC actions
    """
    f_kwargs = {'endpoint': endpoint}

    dapi = DistributedAPI(f=security.get_rbac_actions,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_any',
                          is_async=False,
                          wait_for_complete=True,
                          logger=logger
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def revoke_all_tokens(request):
    """Revoke all tokens."""
    f_kwargs = {}
    nodes = await get_system_nodes()

    dapi = DistributedAPI(f=security.wrapper_revoke_tokens,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='distributed_master',
                          is_async=False,
                          broadcasting=True,
                          wait_for_complete=True,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies'],
                          nodes=nodes
                          )
    data = raise_if_exc(await dapi.distribute_function())
    status = 200
    if type(data) == AffectedItemsWazuhResult and len(data.affected_items) == 0:
        raise_if_exc(WazuhPermissionError(4000, data.message))

    return web.json_response(data=data, status=status, dumps=dumps)


async def get_security_config(request, pretty=False, wait_for_complete=False):
    """Get active security configuration.

    :param pretty: Show results in human-readable format
    :param wait_for_complete: Disable timeout response

    Returns
    -------
    dict
        Security configuration
    """
    f_kwargs = {}

    dapi = DistributedAPI(f=security.get_security_config,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          wait_for_complete=wait_for_complete,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def security_revoke_tokens():
    """Revokes all tokens on all nodes after a change in security configuration."""
    nodes = list()
    try:
        nodes = await get_system_nodes()
    except WazuhInternalError as e:
        if e.code != 3012:  # Cluster is disabled
            raise e

    dapi = DistributedAPI(f=revoke_tokens,
                          request_type='distributed_master' if len(nodes) > 0 else 'local_master',
                          is_async=False,
                          wait_for_complete=True,
                          broadcasting=len(nodes) > 0,
                          logger=logger,
                          nodes=nodes
                          )
    raise_if_exc(await dapi.distribute_function())


async def put_security_config(request, pretty=False, wait_for_complete=False):
    """Update current security configuration with the given one.

    :param pretty: Show results in human-readable format
    :param wait_for_complete: Disable timeout response
    """
    Body.validate_content_type(request, expected_content_type='application/json')
    f_kwargs = {'updated_config': await SecurityConfigurationModel.get_kwargs(request)}

    dapi = DistributedAPI(f=security.update_security_config,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          wait_for_complete=wait_for_complete,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())
    await security_revoke_tokens()

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)


async def delete_security_config(request, pretty=False, wait_for_complete=False):
    """Restore default security configuration.

    :param pretty: Show results in human-readable format
    :param wait_for_complete: Disable timeout response
    """
    f_kwargs = {"updated_config": await SecurityConfigurationModel.get_kwargs(default_security_configuration)}

    dapi = DistributedAPI(f=security.update_security_config,
                          f_kwargs=remove_nones_to_dict(f_kwargs),
                          request_type='local_master',
                          is_async=False,
                          wait_for_complete=wait_for_complete,
                          logger=logger,
                          rbac_permissions=request['token_info']['rbac_policies']
                          )
    data = raise_if_exc(await dapi.distribute_function())
    await security_revoke_tokens()

    return web.json_response(data=data, status=200, dumps=prettify if pretty else dumps)
