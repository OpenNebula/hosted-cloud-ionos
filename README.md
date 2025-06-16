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
Follow the provisioning steps and the detailed guide on how to extract the essential parameters needed to proceed with the OpenNebula deployment.

## Customize the essential parameters

Update the `inventory` values and the `_netplan` files to match the provisioned infrastructure, as described in the above referenced deployment guide. The table below shows the essential parameters that must be updated.

| Description                                 | Variable Names                      | Files/Location                                      |
|---------------------------------------------|-------------------------------------|-----------------------------------------------------|
| Frontend Host IP                            | `ansible_host`                      | `inventory/ionos.yml` (under `frontend: hosts:`)    | 
| KVM Host IPs                            | `ansible_host`                      | `inventory/ionos.yml` (under `node: hosts:`), `/_netplan/*.yaml`    | 
| KVM Host Gateway                            | `network.bridges.br0.routes.to` and `.via`                      | `/_netplan/*.yaml`    | 
| VXLAN PHYDEV                                 | `vn.vxlan.template.PHYDEV`          | `inventory/ionos.yml`                               | 
| pubridge PHYDEV                              | `vn.pubridge.template.PHYDEV`       | `inventory/ionos.yml`                               | 
| VMs Public IP Range                        | `vn.pubridge.template.AR.IP`, `vn.pubridge.template.AR.SIZE` | `inventory/ionos.yml`           | 
| GUI password of `oneadmin`       | `one_pass` | `inventory/ionos.yml`           | 
| IONOS Data Center UUID                      | `ionos_config.data_center_uuid`     | `inventory/ionos.yml`, `group_vars/all.yml`         | 
| IONOSCTL Token                             | `ionosctl.token`                    | `playbooks/files/.ionosctl_token` | 

The below parameters should work fine across different IONOS deployment. Consider these as a few key examples for further potential customization.

| Description                                 | Variable Names                      | Files/Location                                      |
|---------------------------------------------|-------------------------------------|-----------------------------------------------------|
| IONOS Public Bridge Name                    | `ionos_config.public_bridge_name`, `vn.pubridge.template.BRIDGE`, `network.bridges.br0`   | `inventory/ionos.yml`, `group_vars/all.yml`         |
| IONOSCTL Install Path                       | `ionosctl.install_path`             | `inventory/ionos.yml`, `group_vars/all.yml`         |
| IONOSCTL Version                            | `ionosctl.version`                  | `inventory/ionos.yml`, `group_vars/all.yml`         |

## Configure IONOS server networking

After provisioning the infrastructure in the IONOS Cloud, as detailed in the above deployment guide, their network configuration shall be adjusted to this repos automation. Access the CLI of the servers. Remove the generated default netplan configuration on the servers:

```shell
root@217.154.225.209:~# rm /etc/netplan/50-cloud-init.yaml
```

Update the netplan configuration in the `_netplan` folder, by changing the IP addresses which are assigned to the servers. The gateway IPs for the route configurations are assigned by IONOS DHCP server. Copy the contents of the updated `_netplan` folder to the corresponding hosts, for example:

```shell
$ scp _netplan/host02.yaml root@217.154.225.209:/etc/netplan
```

Apply the netplan configurations on each host:

```shell
root@217.154.225.209:~# netplan apply
```

If the servers lose connectivity, the netplan files contain errors. In any case, as a backup option, the servers are always accessible from the IONOS DCD by selecting the server and opening its console from the browser. Worst case, the connectivity can be recovered by restoring the original netplan file (`50-cloud-init.yaml`), or by recreating the HDD or the server. After fixing the issue apply the netplan changes again.

After all these adjustments have been done in the configuration files and network settings, we are ready to start the OpenNebula deployment.

## Deployment and verification

The deployment and verification procedure is highly automated using Ansible and Makefiles. The scripts make use of the configuration files in this repo, overwriting default values in the dependent automation scripts.
Some specific `make` targets for deployment and verification are exposed from the submodule, while also an IONOS-specific installation step is automated.

1. Firstly, to deploy OpenNebula with the inventory file updated above, using the submodule's tooling:

   ```shell
   make main
   ```
   The launched Ansible scripts should finish without any error, and report on the number of changes performed for each hosts. If any error is reported, after the necessary troubleshooting and fixes, the deployment script can be re-executed without further cleanup steps.

1. Next, configure the IONOS-specific tools, launch this command:

   ```shell
   make ionos
   ```
   Similarly, this should finish without any errors. After this step the cloud environment is fully functional.

1. Finally, to verify the deployment using the configurations in the default inventory file:

   ```shell
   make verification
   ```
   If the test fails in any of the steps, after the necessary troubleshooting and fixes, the verification command can be safely re-executed. The final HTML report is only created when all tests have passed.
   The output of the tests are compiled into a HTML report that can be found in path, printed by the automation script.

For more information about the submodule's tooling, refer to the [one-deploy-validation's README.md](https://github.com/OpenNebula/one-deploy-validation/blob/master/README.md) and for detailed documentation on the deployment automation refer to the [one-deploy repo](https://github.com/OpenNebula/one-deploy).

