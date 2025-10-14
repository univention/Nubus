<!--
SPDX-FileCopyrightText: 2025 Univention GmbH
SPDX-License-Identifier: AGPL-3.0-only
-->

# Univention Nubus IAM & Portal

## Introduction

**Modular Identity & Access Management**

Nubus is a modular open-source solution for centralized Identity & Access Management (IAM) in organizations. It enables the management of user identities, access rights, and applications via a central web portal. Users benefit from integrated Single Sign-On (SSO), allowing seamless access to connected systems without repeated logins.

Nubus supports operation in cloud environments, on-premises, and within hybrid IT infrastructures. Built on open standards, the solution is designed for use in privacy-sensitive environments. Univention provides maintenance, support, and project-based services for Nubus.

**Key Features:**

* Central web portal for user management and access control
* Single Sign-On (SSO) for integrated application access
* Self-service functions for users (e.g., password changes, profile updates)
* Management of user accounts, groups, roles, and permissions
* Interfaces for integration with external applications and directories
* Prebuilt integrations for common systems and services
* Scalable architecture for diverse deployment scenarios
* Open-source technology with openly documented APIs
* Suitable for cloud, on-premises, and hybrid environments

**More**

Nubus is designed for organizations with growing needs for centralized identity and access management. It extends existing IT infrastructures with standardized access control and user management.

Learn more about Nubus on our website:
https://www.univention.com/products/nubus/

## About This Repository

The source code of Univention Nubus is distributed across several repositories following the modular architecture of Nubus. This repository collects "meta information" to give an overview about the sources of Nubus and Nubus itself. You won't find any source code here.

## Install Univention Nubus

Univention Nubus supports two deployment methods:
* On *physical hardware or as virtual machine*, one can install Univention Corporate Server (UCS) which includes all modules of Univention Nubus. The process is described in the Operations Manual for UCS: https://docs.software-univention.de/n/en/docs/manual.html
* On *Kubernetes*, one can install Univention Nubus using the provided Helm charts. The process is described in the Nubus for Kubernetes Operations Manual: https://docs.software-univention.de/nubus-kubernetes-operation/latest/en/index.html

## Univention Core Nubus Components and their Repositories

This section only briefly describes the modules of Univention Nubus to link to the main source repositories. More information about the software architecture of Univention Nubus is documented here: https://docs.software-univention.de/nubus-kubernetes-architecture/latest/en/index.html



| Nubus Component                          | Description                                                  | Source Code |
| ---------------------------------------- | ------------------------------------------------------------ | ----------- |
| **Identity Store and Directory Service** | Stores RFC compliant information about Identities/Users and Groups  as well as other information about the IT environment. Is a preconfigured deployment of OpenLDAP including management of LDAP replication, schemas etc.. |             |
| **Identity Provider**                    | Provides Authentication, Federation and partly Authorization services based on open standards, focus is on SAML and OpenID Connect. Supports Federation with other IDPs. Is a preconfigured deployment of Keycloak. |             |
| **Directory Manager**                    | Manages the content of the Identity Store (the OpenLDAP based Directory Service). Provides APIs to management the objects in the Directory Service ("CRUD" operations) and APIs to extend the capabilities (add more attributes to existing objects or add new objects to be managed). Is a python based software implemented by Univention as "Univention Directory Manager" (UDM). |             |
| **Authorization Service**                | API helper to allow fine grained Authorization on APIs. Focused on internal use cases (APIs of Directory Manager, Portal, Self Services and other components utilizing the Univention Management Stack), but also  available to be used by other applications. Uses a preconfigured "Open Policy Agent" as backend. |             |
| **Provisioning Service**                 | Post-processing of events in Univention Nubus, focused on post-processing operations initiated in the Directory Manager. The service is extend-able with plugins and allows to implement  individual, asynchronous backend tasks after events/changes happened - for  example informing an applications API about CRUD operations on users and groups. Uses a preconfigured "NATS" as backend. |             |
| **Intercom Service**                     | Connects backend APIs and their consumers with transparent authentication for different authentication standards/methods. |             |
| **Management UI**                        | User friendly UI to access the functionality of the Directory Manager component and other modules. Focus is on administrative and user helpdesk tasks. Can be extended with additional modules. Is a Python backend implementation  "Univention Management Console" (UMC) with Dojo and Vue.js frontends. |             |
| **End User Self Service**                | User friendly end user UI to access personal information and  settings stored in the Directory Manager component. Allows end users to  change settings like contact information or avatar pictures. Is a frontend to the UMC. |             |
| **Portal**                               | User friendly web portal for end users to get an overview about the applications / services available for this user. Eases the access using web based SSO, integrates the self service, the Management UI and optionally other Web UIs. As APIs to interact with applications to present additional information to the end user (like action items  waiting for the current user in an application). Is mainly a frontend implemented using Vue.js. |             |

## Univention Nubus Extensions and Packaged Integrations

Univention Nubus provides various APIs for extension and preconfiguration during deployments. These are often used to add functionality to connect Applications to the IAM. For better maintainability, such extensions can be bundled as "Packaged Integrations", which combine code like Plugins or Connectors with preconfiguration of Nubus and deployment automation. These packaged integrations are not listed here, entrypoints are:

* Packaged Integrations available for Kubernetes: https://docs.software-univention.de/n/en/docs/packaged-integrations.html
* Packaged Integrations available for UCS: https://www.univention.com/products/app-catalog/

## Contributing

Currently the easiest way to contribute to Univention Nubus is following the [contributing guide](https://github.com/univention/univention-corporate-server/blob/5.2-3/CONTRIBUTING.md) and the [Code of Conduct contains guidelines](https://github.com/univention/univention-corporate-server/blob/5.2-3/CONTRIBUTING.md#code-of-conduct) we expect project participants to adhere to provided on Github.

Information about the software used and the various APIs provided can be found in the [Documentation provided for Sofware Developers](https://docs.software-univention.de/n/en/developers.html#page-developers).

## License

Univention Nubus is built on top of many existing open source projects which use their own licenses. The source code of all parts written by Univention is licensed under the AGPLv3 if not stated otherwise directly in the source code. Please see the individual repositories for more information.
