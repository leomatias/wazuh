/* Copyright (C) 2015-2020, Wazuh Inc.
 * Copyright (C) 2009 Trend Micro Inc.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */

#include "os_auth_wrappers.h"
#include <stddef.h>
#include <stdarg.h>
#include <setjmp.h>
#include <cmocka.h>

SSL_CTX *__wrap_os_ssl_keys(int is_server, const char *os_dir, const char *ciphers, const char *cert, const char *key,
                            const char *ca_cert, int auto_method) {
    check_expected(is_server);
    check_expected(os_dir);
    check_expected(ciphers);
    check_expected(cert);
    check_expected(key);
    check_expected(ca_cert);
    check_expected(auto_method);
    return mock_ptr_type(SSL_CTX *);
}