/* Copyright (C) 2015-2020, Wazuh Inc.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */

#include "sqlite3_wrappers.h"
#include <stddef.h>
#include <stdarg.h>
#include <setjmp.h>
#include <cmocka.h>


int __wrap_sqlite3_bind_int(__attribute__((unused)) sqlite3_stmt *stmt,
                            int index,
                            int value) {
    check_expected(index);
    check_expected(value);

    return mock();
}

int __wrap_sqlite3_bind_int64(__attribute__((unused)) sqlite3_stmt *stmt,
                              int index,
                              sqlite3_int64 value) {
    check_expected(index);
    check_expected(value);

    return mock();
}

int __wrap_sqlite3_bind_text(__attribute__((unused)) sqlite3_stmt* pStmt,
                             int a,
                             const char* b,
                             __attribute__((unused)) int c,
                             __attribute__((unused)) void *d) {
    check_expected(a);
    if (b) check_expected(b);

    return mock();
}

int __wrap_sqlite3_clear_bindings(__attribute__((unused)) sqlite3_stmt* pStmt) {
    return mock();
}

int __wrap_sqlite3_close_v2() {
    return mock();
}

double __wrap_sqlite3_column_double(__attribute__((unused)) sqlite3_stmt *pStmt,
                                    int i) {
    check_expected(i);
    return mock_type(double);
}

int __wrap_sqlite3_column_int(__attribute__((unused)) sqlite3_stmt *pStmt,
                              int i) {
    check_expected(i);
    return mock();
}

sqlite3_int64 __wrap_sqlite3_column_int64(__attribute__((unused)) sqlite3_stmt* stmt,
                                          int iCol) {
    check_expected(iCol);
    return mock();
}

const unsigned char *__wrap_sqlite3_column_text(__attribute__((unused)) sqlite3_stmt *pStmt,
                                                int i) {
    check_expected(i);
    return mock_type(const unsigned char*);

}

const char *__wrap_sqlite3_errmsg() {
    return mock_ptr_type(const char *);
}

int __wrap_sqlite3_exec(__attribute__((unused)) sqlite3* db,                                /* An open database */
                        const char *sql,                                                    /* SQL to be evaluated */
                        __attribute__((unused)) int (*callback)(void*,int,char**,char**),   /* Callback function */
                        __attribute__((unused)) void *arg,                                  /* 1st argument to callback */
                        char **errmsg) {                                                    /* Error msg written here */
    check_expected(sql);
    *errmsg = mock_ptr_type(char *);
    return mock();
}

int __wrap_sqlite3_finalize(__attribute__((unused)) sqlite3_stmt *pStmt) {
    return mock();
}

void __wrap_sqlite3_free(__attribute__((unused)) void* ptr) {
    return;
}

int __wrap_sqlite3_last_insert_rowid(__attribute__((unused)) sqlite3* db){
    return mock();
}

int __wrap_sqlite3_open_v2(const char *filename,                           /* Database filename (UTF-8) */
                           sqlite3 **ppDb,                                 /* OUT: SQLite db handle */
                           int flags,                                      /* Flags */
                           __attribute__((unused)) const char *zVfs) {     /* Name of VFS module to use */
    check_expected(filename);
    check_expected(flags);
    *ppDb = mock_type(sqlite3 *);
    return mock();
}

int __wrap_sqlite3_prepare_v2(__attribute__((unused)) sqlite3 *db,            /* Database handle */
                              __attribute__((unused)) const char *zSql,       /* SQL statement, UTF-8 encoded */
                              __attribute__((unused)) int nByte,              /* Maximum length of zSql in bytes. */
                              __attribute__((unused)) sqlite3_stmt **ppStmt,  /* OUT: Statement handle */
                              const char **pzTail){                          /* OUT: Pointer to unused portion of zSql */
    if(pzTail){
        *pzTail = 0;
    }
    return mock();
}

int __wrap_sqlite3_reset(__attribute__((unused)) sqlite3_stmt *pStmt) {
    return mock();
}

int __wrap_sqlite3_step(__attribute__((unused)) sqlite3_stmt * stmt){
    return mock();
}
