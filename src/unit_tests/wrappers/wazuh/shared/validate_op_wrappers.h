/* Copyright (C) 2015-2020, Wazuh Inc.
 * Copyright (C) 2009 Trend Micro Inc.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */


#ifndef VALIDATE_OP_WRAPPERS_H
#define VALIDATE_OP_WRAPPERS_H

#include <ctype.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int __wrap_getDefine_Int(const char *high_name, const char *low_name, int min, int max);

#endif