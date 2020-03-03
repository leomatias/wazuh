/*
 * Copyright (C) 2015-2019, Wazuh Inc.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation.
 */

#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>
#include <stdio.h>
#include <string.h>

#include "../syscheckd/syscheck.h"


/* redefinitons/wrapping */
void __wrap__mdebug1(const char * file, int line, const char * func, const char *msg, ...) {
    char formatted_msg[OS_MAXSTR];
    va_list args;

    va_start(args, msg);
    vsnprintf(formatted_msg, OS_MAXSTR, msg, args);
    va_end(args);

    check_expected(formatted_msg);
}

void __wrap__minfo(const char * file, int line, const char * func, const char *msg, ...) {
    char formatted_msg[OS_MAXSTR];
    va_list args;

    va_start(args, msg);
    vsnprintf(formatted_msg, OS_MAXSTR, msg, args);
    va_end(args);

    check_expected(formatted_msg);
}

void __wrap__mwarn(const char * file, int line, const char * func, const char *msg, ...)
{
    char formatted_msg[OS_MAXSTR];
    va_list args;

    va_start(args, msg);
    vsnprintf(formatted_msg, OS_MAXSTR, msg, args);
    va_end(args);

    check_expected(formatted_msg);
}

void __wrap__merror_exit(const char * file, int line, const char * func, const char *msg, ...)
{
    char formatted_msg[OS_MAXSTR];
    va_list args;

    va_start(args, msg);
    vsnprintf(formatted_msg, OS_MAXSTR, msg, args);
    va_end(args);

    check_expected(formatted_msg);
}

fdb_t *__wrap_fim_db_init(int memory) {
    check_expected(memory);
    return mock_type(fdb_t*);
}

int __wrap_getDefine_Int() {
    return mock();
}

/* setup/teardowns */
static int setup_group(void **state) {
    fdb_t *fdb = calloc(1, sizeof(fdb_t));

    if(fdb == NULL)
        return -1;

    *state = fdb;

    return 0;
}

static int teardown_group(void **state) {
    fdb_t *fdb = *state;

    free(fdb);

    return 0;
}

/* tests */

void test_fim_initialize(void **state)
{
    fdb_t *fdb = *state;

    expect_value(__wrap_fim_db_init, memory, 0);
    will_return(__wrap_fim_db_init, fdb);

    fim_initialize();

    assert_ptr_equal(syscheck.database, fdb);
}

void test_fim_initialize_error(void **state)
{
    expect_value(__wrap_fim_db_init, memory, 0);
    will_return(__wrap_fim_db_init, NULL);

    expect_string(__wrap__merror_exit, formatted_msg, "(6698): Creating Data Structure: sqlite3 db. Exiting.");

    fim_initialize();

    assert_null(syscheck.database);
}

void test_read_internal(void **state)
{
    (void) state;

    will_return_always(__wrap_getDefine_Int, 1);

    read_internal(0);
}

void test_read_internal_debug(void **state)
{
    (void) state;

    will_return_always(__wrap_getDefine_Int, 1);

    read_internal(1);
}
#ifdef TEST_WINAGENT
int Start_win32_Syscheck();

int __wrap_File_DateofChange(const char * file)
{
    check_expected_ptr(file);
    return mock();
}

int __wrap_Read_Syscheck_Config(const char * file)
{
    check_expected_ptr(file);
    return mock();
}

int __wrap_rootcheck_init(int value)
{
    return mock();
}

void __wrap_os_wait()
{
    function_called();
}

void __wrap_start_daemon()
{
    function_called();
}

void __wrap_read_internal(int debug_level)
{
    function_called();
}

void test_Start_win32_Syscheck_start_fail(void **state)
{
    (void) state;
    
    static char *SYSCHECK_EMPTY[] = { NULL };
    static registry REGISTRY_EMPTY[] = { { NULL, 0, NULL } };
    syscheck.dir = SYSCHECK_EMPTY;
    syscheck.registry = REGISTRY_EMPTY;
    syscheck.disabled = 1;
    
    expect_string(__wrap__mdebug1, formatted_msg, "Starting ...");    

    expect_string(__wrap__minfo, formatted_msg, "(6678): No directory provided for syscheck to monitor.");
    expect_string(__wrap__minfo, formatted_msg, "(6001): File integrity monitoring disabled.");

    will_return_always(__wrap_getDefine_Int, 1);
    expect_string(__wrap_File_DateofChange, file, "ossec.conf");
    
    will_return(__wrap_File_DateofChange, -1);
    expect_string(__wrap__merror_exit, formatted_msg, "(1239): Configuration file not found: 'ossec.conf'.");

    expect_string(__wrap_Read_Syscheck_Config, file, "ossec.conf");
    will_return(__wrap_Read_Syscheck_Config, -1);

    expect_string(__wrap__merror_exit, formatted_msg, "(1202): Configuration error at 'ossec.conf'.");
    
    will_return(__wrap_rootcheck_init, 1);

    expect_value(__wrap_fim_db_init, memory, 0);
    will_return(__wrap_fim_db_init, NULL);

    expect_string(__wrap__merror_exit, formatted_msg, "(6698): Creating Data Structure: sqlite3 db. Exiting.");
 
    expect_function_call(__wrap_os_wait);

    expect_function_call(__wrap_start_daemon);
    Start_win32_Syscheck();
}

void test_Start_win32_Syscheck_start_success(void **state)
{
    (void) state;
    
    static char *SYSCHECK_EMPTY[] = { NULL };
    static registry REGISTRY_EMPTY[] = { { NULL, 0, NULL } };
    syscheck.dir = SYSCHECK_EMPTY;
    syscheck.registry = REGISTRY_EMPTY;
    syscheck.disabled = 0;
    
    char info_msg[OS_MAXSTR];
  
    expect_string(__wrap__mdebug1, formatted_msg, "Starting ...");
    snprintf(info_msg, OS_MAXSTR, "Started (pid: %d).", getpid());
    
    expect_string(__wrap__minfo, formatted_msg, info_msg);

    will_return_always(__wrap_getDefine_Int, 1);
    
    expect_string(__wrap_File_DateofChange, file, "ossec.conf");
    will_return(__wrap_File_DateofChange, 0);

    expect_string(__wrap_Read_Syscheck_Config, file, "ossec.conf");
    will_return(__wrap_Read_Syscheck_Config, 0);

    will_return(__wrap_rootcheck_init, 1);

    expect_value(__wrap_fim_db_init, memory, 0);
    will_return(__wrap_fim_db_init, NULL);

    expect_string(__wrap__merror_exit, formatted_msg, "(6698): Creating Data Structure: sqlite3 db. Exiting.");

    expect_function_call(__wrap_os_wait);

    expect_function_call(__wrap_start_daemon);

    Start_win32_Syscheck();
}

#endif

int main(void) {
    const struct CMUnitTest tests[] = {
            cmocka_unit_test(test_fim_initialize),        
            cmocka_unit_test(test_fim_initialize),
            cmocka_unit_test(test_fim_initialize_error),
            cmocka_unit_test(test_read_internal),
            cmocka_unit_test(test_read_internal_debug),
        /* Windows specific tests */
        #ifdef TEST_WINAGENT
            cmocka_unit_test(test_Start_win32_Syscheck_start_fail),
            cmocka_unit_test(test_Start_win32_Syscheck_start_success),
        #endif
    };

    return cmocka_run_group_tests(tests, setup_group, teardown_group);
}