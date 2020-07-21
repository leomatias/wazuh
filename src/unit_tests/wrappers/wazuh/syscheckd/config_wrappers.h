/* Copyright (C) 2015-2020, Wazuh Inc.
 * Copyright (C) 2009 Trend Micro Inc.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */


#ifndef CREATE_DB_WRAPPERS_H
#define CREATE_DB_WRAPPERS_H

#include "../../../../syscheckd/syscheck.h"
#include "../../../../external/cJSON/cJSON.h"

void __wrap_free_whodata_event(whodata_evt *w_evt);

cJSON * __wrap_getRootcheckConfig();

cJSON * __wrap_getSyscheckConfig();

cJSON * __wrap_getSyscheckInternalOptions();

#endif