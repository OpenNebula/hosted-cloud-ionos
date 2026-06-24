
# script and templates for netplan config
## Purpose
- This script helps to create netplan config for OpenNebula-hosts, created and used with IONOS-DCD
---

## Requirements - what you need:
### you have created two debian12-servers in IONOS-DCD according docu:
- https://docs.opennebula.io/7.0/solutions/ecosystem/hosted_cloud_providers/ionos/
- During the installation, youu checked out this repo 
- 1) https://github.com/OpenNebula/cloud-hosted-ionos

- what you also need (from this repo abov, subdir create_neplan):
- netplan-config - templates in directory: _netplan_templates/ 
  - files: h1.yaml, fe.yaml, h2.yaml

- important: .env  == config - file - see comments there !!
- see also: .env_template in repo_dir from repo 1):  hosted-cloud-ionos/ionos_server_4ons/.env_template

- use make with rquirements.txt:
- make help
  - Targets:
  - make venv     - create virtual environment
  - make install  - install dependencies into virtual environment
  - make run      - run create_netplan_cfg.py
  - make clean    - remove virtual environment

### output-files will e created:
- h1.yaml   # netplan - config for server 1
- fe.yaml   # netplan - config for server 1 (also frontend - server) 
- h2.yaml   # netplan - config for server 2 

### how to activate netplan - configs
- use ssh-identity writen from  
  ../hosted-cloud-ionos/ionos_server_4ons/create_server_4ons.py
  (this may be the cloned repo - see above)
- ssh-identity is written in the path, where you have started this script
- or: use your own ssh-identity (if you manually created the two DCD-Servers)

- put configs on the relating server, directory: /etc/netplan
- remove old configs from (example:  /etc/netplan/50-cloud-init.yaml)
- netplan try     # try config, rollback possible
- netplan apply   # apply config



