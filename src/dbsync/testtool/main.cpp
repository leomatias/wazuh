/*
 * Wazuh DBSYNC
 * Copyright (C) 2015-2020, Wazuh Inc.
 * June 11, 2020.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation.
 */

#include <fstream>
#include <stdio.h>
#include <json.hpp>
#include "dbsync.h"
#include "cmdArgsHelper.h"

struct CJsonDeleter
{
    void operator()(cJSON* json)
    {
        cJSON_Delete(json);
    }
};

struct CharDeleter
{
    void operator()(char* json)
    {
        cJSON_free(json);
    }
};

static std::string currentSnapToString(const std::string& inputFile)
{
    std::ifstream snapshotFileIdx{ inputFile };
    const nlohmann::json jsonSnapshotFile { nlohmann::json::parse(snapshotFileIdx) };   
    std::string jsonSnapshotContent{ std::move(jsonSnapshotFile[0].dump()) };
    return jsonSnapshotContent;
}

int main(int argc, char* argv[])
{
    CmdLineArgs cmdLineArgs(argc, argv);

    if (!cmdLineArgs.argsAreOK())
    {
        cmdLineArgs.showHelp();
    }
    else
    {
        std::vector<std::string> snapshots;
        cmdLineArgs.snapshotList(snapshots);

        // dbsync configuration data 
        std::ifstream configFile{ cmdLineArgs.configFile() };
        const nlohmann::json jsonConfigFile { nlohmann::json::parse(configFile) };
        const std::string dbName{ jsonConfigFile[0]["db_name"] };
        const std::string dbType{ jsonConfigFile[0]["db_type"] };
        const std::string hostType{ jsonConfigFile[0]["host_type"] };        
        const std::string persistance{ jsonConfigFile[0]["persistance"] };
        const std::string sqlStmt{ jsonConfigFile[0]["sql_statement"] };

        auto handle 
        { 
            dbsync_initialize((hostType.compare("0") == 0) ? HostType::MANAGER : HostType::AGENT, 
                              (dbType.compare("0") == 0) ? DbEngineType::SQLITE3 : DbEngineType::UNDEFINED, 
                              dbName.c_str(),
                              sqlStmt.c_str()) 
        };

        if(0 != handle)
        {
            // Let's take the input json list and apply the changes to the db
            for (size_t idx = 0; idx < snapshots.size(); ++idx) 
            {
                const std::string snapshotsIdxFile{ snapshots[idx] };
                const std::unique_ptr<cJSON, CJsonDeleter> currentSnapshot
                { 
                    cJSON_Parse(currentSnapToString(snapshotsIdxFile).c_str())
                };
                cJSON* snapshotLambda{ nullptr };
                if(0 == dbsync_update_with_snapshot(handle, currentSnapshot.get(), &snapshotLambda))
                {
                    // Create and flush snapshot diff data in files like: snapshot_<#idx>.json
                    std::cout << "Processing file: " << snapshots[idx] << std::endl;
                    std::stringstream oFileName;
                    oFileName << "snapshot_" << idx << ".json";
                    const std::string outputFileName{ cmdLineArgs.outputFolder()+"/"+oFileName.str() };
                    std::ofstream outputFile{ outputFileName };
                    const std::unique_ptr<char, CharDeleter> snapshotDiff{ cJSON_Print(snapshotLambda) };
                    outputFile << snapshotDiff.get() << std::endl;
                    outputFile.close();
                    dbsync_free_result(&snapshotLambda);                 
                }
            }
            std::cout << "Resulting files are located in the "<< cmdLineArgs.outputFolder() << "folder" << std::endl;
        }
    }
    return 0;
}