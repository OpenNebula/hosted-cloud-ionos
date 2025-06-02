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

## Inventory/Execution

> [!NOTE]
> It's exactly the same as with `one-deploy`.

1. Inventories are kept in the `./inventory/` directory.

1. Some specific make targets for deployment and verification are exposed from the submodule. To deploy with the default inventory file, using the submodule's tooling:

   ```shell
   make main
   ```

1. To verify the deployment using the configurations in the default inventory file:

   ```shell
   make verification
   ```

For more information about the submodule's tooling, refer to its [README.md](https://github.com/OpenNebula/one-deploy-validation/blob/master/README.md).

