

### purpose of the script:
### create two debian12-servers in IONOS-DCD according docu:
https://docs.opennebula.io/7.0/solutions/ecosystem/hosted_cloud_providers/ionos/

### Requirements - before you start use make:
- make help - Available targets:
  - venv       - Create virtual environment
  - install    - Install venv and dependencies
  - test       - Test the environment
  - run        - Run the script (use snr=1 or snr=2 to specify server number)
  - clean      - Remove virtual environment and cache files

- important: .env  == config - file - see comments there !!

### two script-calls needed:
- make run snr=1
- make run snr=2
- creation of one server needs 6 - 7 minutes
- simple start with script: start_create_2servers.sh

### ssh-check after server creation:
- ssh -i  .ssh_ons/id_rsa root@IP_server1  uptime
- ssh -i  .ssh_ons/id_rsa root@IP_server2  uptime
- (also .ssh_on2 is possible)

### what else will be created:
#### IP forwarding allowed on all hosts, check with: 
- ssh -i  .ssh_ons/id_rsa root@IP_server1  cat /proc/sys/net/ipv4/ip_forward
- ssh -i  .ssh_ons/id_rsa root@IP_server2  cat /proc/sys/net/ipv4/ip_forward - (result must be value 1 for both)

- Cloud-Init1.log     # log from server1 - for debugging issus, if needed
- Cloud-Init2.log     # log from server2 - for debugging issus, if needed

#### directory with ssh-keys - server1
- .ssh_ons/       # directory wiith ssh-keys - server1
- .ssh_ons2/      # directory wiith ssh-keys - server2


