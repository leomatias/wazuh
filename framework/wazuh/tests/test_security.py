#!/usr/bin/env python
# Copyright (C) 2015-2020, Wazuh Inc.
# Created by Wazuh, Inc. <info@wazuh.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2


import glob
import os
from importlib import reload
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from yaml import safe_load

from wazuh.core.exception import WazuhError

test_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'security/')

# Params

security_cases = list()
rbac_cases = list()
os.chdir(test_data_path)

for file in glob.glob('*.yml'):
    with open(os.path.join(test_data_path + file)) as f:
        tests_cases = safe_load(f)

    for function_, test_cases in tests_cases.items():
        for test_case in test_cases:
            if file != 'rbac_catalog.yml':
                security_cases.append((function_, test_case['params'], test_case['result']))
            else:
                rbac_cases.append((function_, test_case['params'], test_case['result']))


def create_memory_db(sql_file, session):
    with open(os.path.join(test_data_path, sql_file)) as f:
        for line in f.readlines():
            line = line.strip()
            if '* ' not in line and '/*' not in line and '*/' not in line and line != '':
                session.execute(line)
                session.commit()


@pytest.fixture(scope='function')
def db_setup():
    with patch('wazuh.common.ossec_uid'), patch('wazuh.common.ossec_gid'):
        with patch('sqlalchemy.create_engine', return_value=create_engine("sqlite://")):
            with patch('shutil.chown'), patch('os.chmod'):
                with patch('api.constants.SECURITY_PATH', new=test_data_path):
                    import wazuh.rbac.orm as orm
                    reload(orm)
                    import wazuh.rbac.decorators as decorators
                    from wazuh.tests.util import RBAC_bypasser

                    decorators.expose_resources = RBAC_bypasser
                    from wazuh import security
                    from wazuh.core.results import WazuhResult
                    from wazuh.core import security as core_security
    try:
        create_memory_db('schema_security_test.sql', orm._Session())
    except OperationalError:
        pass

    yield security, WazuhResult, core_security


def affected_are_equal(target_dict, expected_dict):
    return target_dict['affected_items'] == expected_dict['affected_items']


def failed_are_equal(target_dict, expected_dict):
    if len(target_dict['failed_items'].keys()) == 0 and len(expected_dict['failed_items'].keys()) == 0:
        return True
    result = False
    for target_key, target_value in target_dict['failed_items'].items():
        for expected_key, expected_value in expected_dict['failed_items'].items():
            result = expected_key in str(target_key) and set(target_value) == set(expected_value)
            if result:
                break

    return result


@pytest.mark.parametrize('security_function, params, expected_result', security_cases)
def test_security(db_setup, security_function, params, expected_result):
    """Verify the entire security module.

    Parameters
    ----------
    db_setup : callable
        This function creates the rbac.db file.
    security_function : list of str
        This is the name of the tested function.
    params : list of str
        Arguments for the tested function.
    expected_result : list of dict
        This is a list that contains the expected results .
    """
    try:
        security, _, _ = db_setup
        result = getattr(security, security_function)(**params).to_dict()
        assert affected_are_equal(result, expected_result)
        assert failed_are_equal(result, expected_result)
    except WazuhError as e:
        assert str(e.code) == list(expected_result['failed_items'].keys())[0]

@pytest.mark.parametrize('security_function, params, expected_result', rbac_cases)
def test_rbac_catalog(db_setup, security_function, params, expected_result):
    """Verify RBAC catalog functions.

    Parameters
    ----------
    db_setup : callable
        This function creates the rbac.db file.
    security_function : list of str
        This is the name of the tested function.
    params : list of str
        Arguments for the tested function.
    expected_result : list of dict
        This is a list that contains the expected results .
    """
    security, _, _ = db_setup
    final_params = dict()
    for param, value in params.items():
        if value.lower() != 'none':
            final_params[param] = value
    result = getattr(security, security_function)(**final_params).to_dict()
    assert result['result'] == expected_result


def test_revoke_tokens(db_setup):
    """Checks that the return value of revoke_tokens is a WazuhResult."""
    with patch('wazuh.core.security.change_secret', side_effect=None):
        security, WazuhResult, _ = db_setup
        result = security.revoke_current_user_tokens()
        assert isinstance(result, WazuhResult)


@pytest.mark.parametrize('role_list, expected_users', [
    ([100, 101], {'100', '103', '102'}),
    ([102], {'104'}),
    ([102, 103, 104], {'101', '104', '102'})
])
def test_check_relationships(db_setup, role_list, expected_users):
    """Check that the relationship between role and user is correct according to
    `schema_security_test.sql`.

    Parameters
    ----------
    role_list : list
        List of role IDs.
    expected_users : set
        Expected users.
    """
    _, _, core_security = db_setup
    assert core_security.check_relationships(roles=[{'id': role_id} for role_id in role_list]) == expected_users


@pytest.mark.parametrize('role_list, user_list, expected_users', [
    ([104], None, {'101', '104', '102'}),
    ([102, 103], ['100'], {'101', '104', '100'}),
    ([], ['1', '2'], {'1', '2'})
])
def test_invalid_users_tokens(db_setup, role_list, user_list, expected_users):
    """Check that the argument passed to `TokenManager.add_user_rules` formed by `roles` and
    `users` is correct.

    Parameters
    ----------
    role_list : list
        List of role IDs.
    user_list : list
        List of users.
    expected_users : set
        Expected users.
    """
    with patch('wazuh.security.TokenManager.add_user_rules') as TM_mock:
        _, _, core_security = db_setup
        core_security.invalid_users_tokens(roles=[{'id': role_id} for role_id in role_list], users=user_list)
        related_users = TM_mock.call_args.kwargs['users']
        assert set(related_users) == expected_users
