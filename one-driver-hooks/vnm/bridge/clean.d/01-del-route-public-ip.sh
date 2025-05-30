#!/bin/bash

export PATH=$HOME/ionosctl:$PATH

# --force is required to override the existing config file, if it exists
ionosctl login --force --token 'TOKEN_PLACEHOLDER'

ionosctl nic update --datacenter-id  7ff493e4-c722-4429-80f3-0c90564c26c3\
 --server-id d84f8a6b-bee0-4b24-82d5-4c28ea97e84d\
 --nic-id 07f0a82e-0f41-47d2-834d-729748399608\
 --ips '217.154.225.209'

# Note: NOPASSWORD rule is needed for the oneadmin to add/delete routes
sudo ip route del 217.154.225.193/32 dev br0

ionosctl logout
