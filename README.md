
![one-ionos](https://github.com/user-attachments/assets/523b4b3b-bc48-40b6-b857-99ee023253d5)

# Deploying OpenNebula as a Hosted Cloud on IONOS

This repository contains the needed code and documentation to perform an OpenNebula deployment and configuration as a Hosted Cloud on IONOS bare-metal resources. It extends the [one-deploy-validation](https://github.com/OpenNebula/one-deploy-validation) repository, which is added as a git submodule.

## Table of Contents

- [OpenNebula Cloud Hosted on IONOS Cloud](#opennebula-cloud-hosted-on-ionos-cloud)
- [Requirements](#requirements)
- [Infrastructure Provisioning](#infrastructure-provisioning)
- [Required Parameters](#required-parameters)
- [Configure IONOS Server Networking](#configure-ionos-server-networking)
- [Deployment and Validation](#deployment-and-validation)

## Requirements

1. Install `hatch`

   ```shell
   pip install hatch
   ```

1. Initialize the dependent `one-deploy-validation` and `one-deploy` submodule

   ```shell
   git submodule update --init --remote --merge
   ```

1. Install the `opennebula.deploy` collection with dependencies using the submodule's tooling:

   ```shell
   make submodule-requirements
   ```

## Infrastructure Provisioning

A detailed guide to provision the required reference infrastructure is published in [IONOS - OpenNebula Deployment Guide](https://docs.opennebula.io/7.0/solutions/hosted_cloud_providers/ionos_opennebula/).
Follow the provisioning steps and extract the requiremed parameters needed to proceed with the OpenNebula deployment.

## Required Parameters

Update the [inventory](./inventory) values and the [_netplan](./_netplan) files to match the provisioned infrastructure.

| Description                    | Variable Names                                              | Files/Location                                                                             |
|-------------------------------|-------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| Frontend Host IP              | `ansible_host`                                              | [`inventory/ionos.yml`](./inventory/ionos.yml)                                              |
| KVM Host IPs                  | `ansible_host`                                              | [`inventory/ionos.yml`](./inventory/ionos.yml) , [`_netplan/*.yaml`](./_netplan)            |
| KVM Host Gateway              | `network.bridges.br0.routes.to` and `.via`                  | [`_netplan/*.yaml`](./_netplan)                                                             |
| VXLAN PHYDEV                  | `vn.vxlan.template.PHYDEV`                                  | [`inventory/ionos.yml`](./inventory/ionos.yml)                                              |
| pubridge PHYDEV               | `vn.pubridge.template.PHYDEV`                               | [`inventory/ionos.yml`](./inventory/ionos.yml)                                              |
| VMs Public IP Range           | `vn.pubridge.template.AR.IP`, `vn.pubridge.template.AR.SIZE`| [`inventory/ionos.yml`](./inventory/ionos.yml)                                              |
| GUI password of `oneadmin`    | `one_pass`                                                  | [`inventory/ionos.yml`](./inventory/ionos.yml)                                              |
| IONOS Data Center UUID        | `ionos_config.data_center_uuid`                             | [`inventory/ionos.yml`](./inventory/ionos.yml), [`group_vars/all.yml`](./group_vars/all.yml)|
| IONOSCTL Token                | `ionosctl.token`                                            | [`playbooks/files/.ionosctl_token`](./playbooks/files/.ionosctl_token)                      |


**Optional customization parameters**:

| Description                      | Variable Names                                                                   | Files/Location                                                                 |
|----------------------------------|----------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| IONOS Public Bridge Name         | `ionos_config.public_bridge_name`, `vn.pubridge.template.BRIDGE`, `network.bridges.br0` | [`inventory/ionos.yml`](./inventory/ionos.yml), [`group_vars/all.yml`](./group_vars/all.yml) |
| IONOSCTL Install Path            | `ionosctl.install_path`                                                         | [`inventory/ionos.yml`](./inventory/ionos.yml), [`group_vars/all.yml`](./group_vars/all.yml) |
| IONOSCTL Version                 | `ionosctl.version`                                                              | [`inventory/ionos.yml`](./inventory/ionos.yml), [`group_vars/all.yml`](./group_vars/all.yml) |

## Configure IONOS Server Networking

After provisioning, adjust the default network configuration in each of the hosts:

1. SSH into the host and remove the default netplan config:

   ```shell
   root@h1:~# rm /etc/netplan/50-cloud-init.yaml
   ```

1. Copy the updated configuration to the host:

   ```shell
   $ scp _netplan/h1.yaml root@h1:/etc/netplan
   ```

1. Allow IP forwarding on all hosts (and add the `net.ipv4.ip_forward=1` line to `/etc/sysctl.conf` to make it persistent across reboots):

   ```shell
   root@h1:~# sysctl -w net.ipv4.ip_forward=1
   ```

1. Apply the netplan configuration:

   ```shell
   root@h1:~# netplan apply
   ```

If connectivity is lost, revert via IONOS DCD console access by restoring the original netplan file (`50-cloud-init.yaml`) or recreating the host.

## Deployment and Validation

Use the provided Makefile commands to automate deployment and testing:

1. Deploy OpenNebula:

   ```shell
   make deployment
   ```
   The launched Ansible scripts should finish without any error, and report on the number of changes performed for each hosts. If any error is reported, after the necessary troubleshooting and fixes, the deployment script can be re-executed without further cleanup steps.

1. Configure IONOS-specific components:

   ```shell
   make ionos
   ```
   Similarly, this should finish without any errors. After this step the cloud environment is fully functional.

1. Test the deployment:

   ```shell
   make validation
   ```
   If the test fails in any of the steps, after the necessary troubleshooting and fixes, the validation command can be safely re-executed. The final HTML report is only created when all tests have passed.
   The output of the tests are compiled into a HTML report that can be found in path, printed by the automation script.

For more information about the submodule's tooling, refer to the [one-deploy-validation's README.md](https://github.com/OpenNebula/one-deploy-validation/blob/master/README.md) and for detailed documentation on the deployment automation refer to the [one-deploy repo](https://github.com/OpenNebula/one-deploy).

## Extending with a New Host

To extend the deployment with a new host, follow the same steps as descibed above, in summary:

1. Provision the new host as described in [Infrastructure Provisioning](#infrastructure-provisioning),
1. Save the required parameters and adapt the files to match the provisioned infra, as shown in [Required Parameters](#required-parameters),
1. Configure networking the same way as for all hosts, following [Configure IONOS Server Networking](#configure-ionos-server-networking),
1. Execute the automation commands to deploy and test the cloud, as descibred in [Deployment and Validation](#deployment-and-validation).
