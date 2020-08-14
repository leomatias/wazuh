# Wazuh

[![Slack](https://img.shields.io/badge/slack-join-blue.svg)](https://wazuh.com/community/join-us-on-slack/)
[![Email](https://img.shields.io/badge/email-join-blue.svg)](https://groups.google.com/forum/#!forum/wazuh)
[![Documentation](https://img.shields.io/badge/docs-view-green.svg)](https://documentation.wazuh.com)
[![Documentation](https://img.shields.io/badge/web-view-green.svg)](https://wazuh.com)
[![Coverity](https://scan.coverity.com/projects/10992/badge.svg)](https://scan.coverity.com/projects/wazuh-wazuh)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)](https://twitter.com/wazuh)
[![YouTube](https://img.shields.io/youtube/views/peTSzcAueEc?style=social)](https://www.youtube.com/watch?v=peTSzcAueEc)


Wazuh helps you to gain deeper security visibility into your infrastructure by monitoring hosts at an operating system and application level. This solution, based on lightweight multi-platform agents, provides the following capabilities:

- **Log management and analysis:** Wazuh agents read operating system and application logs, and securely forward them to a central manager for rule-based analysis and storage.
- **File integrity monitoring:** Wazuh monitors the file system, identifying changes in content, permissions, ownership, and attributes of files that you need to keep an eye on.
- **Intrusion and anomaly detection:** Agents scan the system looking for malware, rootkits or suspicious anomalies. They can detect hidden files, cloaked processes or unregistered network listeners, as well as inconsistencies in system call responses.
- **Policy and compliance monitoring:** Wazuh monitors configuration files to ensure they are compliant with your security policies, standards or hardening guides. Agents perform periodic scans to detect applications that are known to be vulnerable, unpatched, or insecurely configured.

This diverse set of capabilities is provided by integrating OSSEC, OpenSCAP and Elastic Stack, making them work together as a unified solution, and simplifying their configuration and management.

Wazuh provides an updated log analysis ruleset, and a RESTful API that allows you to monitor the status and configuration of all Wazuh agents.

Wazuh also includes a rich web application (fully integrated as a Kibana app), for mining log analysis alerts and for monitoring and managing your Wazuh infrastructure.

## Orchestration

*In development*

* [Puppet scripts](https://documentation.wazuh.com/current/deploying-with-puppet/index.html) for automatic Wazuh deployment and configuration.

* [Docker containers](https://documentation.wazuh.com/current/docker/index.html) to virtualize and run your Wazuh manager and an all-in-one integration with ELK Stack.

## Branches

* `master` branch on correspond to the last Wazuh stable version.
* `develop` branch contains the latest code, be aware of possible bugs on this branch.

## Software and libraries used

* Modified version of Zlib and a embedded part of OpenSSL (SHA1, SHA256, SHA512, AES and Blowfish libraries).
* OpenSSL Project for use in the OpenSSL Toolkit (http://www.openssl.org/).
* Cryptographic software written by Eric Young (eay@cryptsoft.com).
* Software developed by the Zlib project (Jean-loup Gailly and Mark Adler).
* Software developed by the cJSON project (Dave Gamble).
* Curl project (https://curl.haxx.se/).
* Software developed by the SQLite project (https://www.sqlite.org/index.html).
* A embedded part of the Berkeley DB library (https://github.com/berkeleydb/libdb).
* CPython interpreter by Guido van Rossum and the Python Software Foundation (https://www.python.org).
* PyPi packages: [azure-storage-blob](https://github.com/Azure/azure-storage-python), [boto3](https://github.com/boto/boto3), [cryptography](https://github.com/pyca/cryptography), [docker](https://github.com/docker/docker-py), [pytz](https://pythonhosted.org/pytz/), [requests](http://python-requests.org/) and [uvloop](http://github.com/MagicStack/uvloop).

## Documentation

* [Full documentation](http://documentation.wazuh.com)
* [Wazuh installation guide](https://documentation.wazuh.com/current/installation-guide/index.html)

## Get involved

Become part of the [Wazuh's community](https://wazuh.com/community/) to learn from other users, participate in discussions, talk to our developers and contribute to the project.

If you want to contribute to our project please don’t hesitate make pull-requests, submit issues or send commits, we will review all your questions.

You can also join our [Slack #community channel](https://wazuh.com/community/join-us-on-slack/) and [mailing list](https://groups.google.com/d/forum/wazuh) by sending an email to [wazuh+subscribe@googlegroups.com](mailto:wazuh+subscribe@googlegroups.com), to ask questions and participate in discussions.

## Online content and social networks

Stay up to date on news, releases, engineering articles and more.

* [Linkedin](https://www.linkedin.com/company/wazuh)
* [YouTube](https://www.youtube.com/c/wazuhsecurity)
* [Twitter](https://twitter.com/wazuh)
* [Wazuh blog](https://wazuh.com/blog/)
* [Slack #announcements channel](https://wazuh.com/community/join-us-on-slack/)

## Authors

Wazuh Copyright (C) 2015-2020 Wazuh Inc. (License GPLv2)

Based on the OSSEC project started by Daniel Cid.

## References

* [Wazuh website](http://wazuh.com)
