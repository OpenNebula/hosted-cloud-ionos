# OpenNebula on IONOS Cloud

Deployment and configuration specific to IONOS Cloud. This repo is extends on the [one-deploy-validation](https://github.com/OpenNebula/one-deploy-validation).

## Requirements

> [!NOTE]
> If Makefile is used then it will create python virtual environments using `hatch` (on demand).

1. Install `hatch`

   ```shell
   pip install hatch
   ```

1. Initialize the dependent `one-deploy-validation` submodule

   ```shell
   git submodule update --init
   ```

1. Install the `opennebula.deploy` collection with dependencies using the submodule's tooling:

   ```shell
   make submodule-requirements
   ```

## Infrastructure provisioning

A detailed guide to provision the required reference infrastructure is published in [IONOS - OpenNebula Deployment Guide](https://docs.google.com/document/d/e/2PACX-1vR7fsXGSXHoKeeFGbM92KLCNDqa0PFOQEQL1iDwYsMct6lIAbAll46kJ4V33CdBcuic80ax-84mynqC/pub).

## Customize the values for the provisioned infrastructure

Update the `inventory` values and the `_netplan` files to match the provisioned infrastructure, as described in the above referenced deployment guide. The table below shows the main parameters that should be updated.

| Description                                 | Variable Names                      | Files/Location                                      | Change is Mandatory/Optional |
|---------------------------------------------|-------------------------------------|-----------------------------------------------------|--------------------|
| Frontend Host IP                            | `ansible_host`                      | `inventory/ionos.yml` (under `frontend: hosts:`)    | Mandatory         |
| KVM Host IPs                            | `ansible_host`                      | `inventory/ionos.yml` (under `node: hosts:`), `/_netplan/*.yaml`    | Mandatory         |
| KVM Host Gateway                            | `network.bridges.br0.routes.to` and `.via`                      | `/_netplan/*.yaml`    | Mandatory         |
| VXLAN PHYDEV                                 | `vn.vxlan.template.PHYDEV`          | `inventory/ionos.yml`                               | Mandatory         |
| pubridge PHYDEV                              | `vn.pubridge.template.PHYDEV`       | `inventory/ionos.yml`                               | Mandatory      |
| VMs Public IP Range                        | `vn.pubridge.template.AR.IP`, `vn.pubridge.template.AR.SIZE` | `inventory/ionos.yml`           | Mandatory                    |
| IONOS Data Center UUID                      | `ionos_config.data_center_uuid`     | `inventory/ionos.yml`, `group_vars/all.yml`         | Mandatory         |
| IONOSCTL Token                             | `ionosctl.token`                    | `playbooks/files/.ionosctl_token` | Mandatory         |
| IONOS Public Bridge Name                    | `ionos_config.public_bridge_name`, `vn.pubridge.template.BRIDGE`, `network.bridges.br0`   | `inventory/ionos.yml`, `group_vars/all.yml`         | Optional         |
| IONOSCTL Install Path                       | `ionosctl.install_path`             | `inventory/ionos.yml`, `group_vars/all.yml`         | Optional          |
| IONOSCTL Version                            | `ionosctl.version`                  | `inventory/ionos.yml`, `group_vars/all.yml`         | Optional          |

After all these adjustments have been done in the configuration files, we are ready to start the OpenNebula deployment.

## Deployment and verification

1. Some specific make targets for deployment and verification are exposed from the submodule. To deploy with the default inventory file, using the submodule's tooling, and configure the IONOS-specific deployment, launch these commands:

   ```shell
   make main
   make ionos
   ```

1. To verify the deployment using the configurations in the default inventory file:

   ```shell
   make verification
   ```

For more information about the submodule's tooling, refer to its [README.md](https://github.com/OpenNebula/one-deploy-validation/blob/master/README.md).

