# OpenNebula on IONOS Cloud

Deployment and configuration specific to IONOS Cloud. This repo is following the structure [engineering-deploy](https://github.com/OpenNebula/engineering-deploy).

## Requirements

> [!NOTE]
> If Makefile is used then it will create python virtual environments using `hatch` (on demand).

1. Install `hatch`

   ```shell
   pip install hatch
   ```

   or

   ```shell
   pipx install hatch
   ```

   or use any other method you see fit

2. Install the `opennebula.deploy` collection with dependencies

   ```shell
   make requirements
   ```

   if you'd like to pick specific branch (instead of `master`), tag or a custom fork

   ```shell
   make requirements ONE_DEPLOY_URL:=git+https://github.com/OpenNebula/one-deploy.git,release-1.2.1
   ```

   the `one-deploy` repository checkout should be available in `~/.ansible/collections/ansible_collections/opennebula/deploy/`


   ## Inventory/Execution
   
   > [!NOTE]
   > It's exactly the same as with `one-deploy`.
   
   1. Inventories are kept in the `./inventory/` directory.
   
   2. To execute `ansible-playbook` you can run
   
      ```shell
      make I=inventory/ionos.yml main
      ```
   
      all the normal targets are available by default
   
      - [infra](./playbooks/infra.yml)
      - [main](./playbooks/main.yml)
      - [pre](./playbooks/pre.yml)
      - [site](./playbooks/site.yml)
   