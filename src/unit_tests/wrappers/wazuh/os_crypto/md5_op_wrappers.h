/* Copyright (C) 2015-2020, Wazuh Inc.
 * Copyright (C) 2009 Trend Micro Inc.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */


#ifndef MD5_OP_WRAPPERS_H
#define MD5_OP_WRAPPERS_H

#include <string.h>
#include <sys/types.h>

typedef char os_md5[33];
typedef char os_sha1[41];
typedef char os_sha256[65];

int __wrap_OS_MD5_File(const char *fname, os_md5 output, int mode);

int __wrap_OS_MD5_SHA1_SHA256_File(const char *fname, const char *prefilter_cmd, os_md5 md5output, os_sha1 sha1output,
                                   os_sha256 sha256output, int mode, size_t max_size);

#endif