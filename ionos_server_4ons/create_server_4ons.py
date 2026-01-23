#!/home/pydev/.venv/bin/python

from __future__ import print_function
import time
from datetime import datetime
import ionoscloud
from ionoscloud.rest import ApiException
from dotenv import dotenv_values
import base64
from pathlib import Path
import os
import argparse
from ruamel.yaml import YAML

parser = argparse.ArgumentParser(description='Script creates 2 (debian-12) servers in IONOS-DCD for use with OpenNebula')
parser.add_argument('-snr',  type=int, choices=[1,2], required=True, help='server number to add')
args = parser.parse_args()

servernumber = args.snr 

print("#" * 77)
print("####### Creating server with servernumber: ",servernumber)
print("#" * 77)

# Defining the host is optional and defaults to https://api.ionos.com/cloudapi/v6
configuration = ionoscloud.Configuration(
    host = 'https://api.ionos.com/cloudapi/v6',
)

config = {
    **dotenv_values(".env"),  # load shared development variables
}

configuration.token    = config['token']
datacenter_id          = config['dc_id']

lan_id                 = int(config['lan_id'])
lan2_id                = int(config['lan2_id'])

h_name                 = config['h_name']
h_cores                = config['h_cores']
h_ram                  = config['h_ram']
h_disk_size            = config['h_disk_size']
h_passw                = config['h_root_password']
# <------- 
#

# --------------------------------------------------------------------------
# functions:
# --------------------------------------------------------------------------

# get ip and gateway-ip for servernumber
def get_servers():
    zserver = 0

    with ionoscloud.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = ionoscloud.ServersApi(api_client)
        # datacenter_id = 'datacenter_id_example' # str | The unique ID of the data center.
        try:
            # List servers 
            servers = api_instance.datacenters_servers_get(datacenter_id, depth=1)
            print(f"{'nr:  '} {'server_name':<15} {'server_id':<39} {'server_state':<12}")
            for server in servers.items:
                zserver = zserver + 1
                print(f"{zserver:<5} {server.properties.name:<15} {server.id:<39} {server.metadata.state:<12}")

        except ApiException as e:
            print('Exception when calling ServersApi.datacenters_servers_get: %s\n' % e)

        print("-" * 77)
        if zserver == 0:
            print(f"{zserver} {'servers found, you can create new servers'}")
        if zserver == 2:
            print(f"{zserver} {'servers found, you can not create new servers!'}")
            print(f"{'Note: First you have to delete the old servers, then you can not create new servers'}")
            print (">>> now exit!")
            exit(2)

    return zserver


# --------------------------------------------------------------------------
# get ip and gateway-ip for servernumber
def get_ip(servernumber):
    ip_found = '0'
    idx = servernumber -1

    with ionoscloud.ApiClient(configuration) as api_client:
        api_instance = ionoscloud.IPBlocksApi(api_client)   # Create an instance of the API class
        try:
            api_response = api_instance.ipblocks_get()      # List IP blocks
        except ApiException as e:
            print('Exception when calling IPBlocksApi.ipblocks_get: %s\n' % e)

        for ipblock in api_response.items:
            ipblock_d = api_instance.ipblocks_find_by_id(ipblock.id)

            if ipblock_d.properties.name == 'booked_for_servers':   # and servernumber == 2:
                print("=" * 55)
                print(ipblock_d.properties.name,'found, +ok',"servernumber", servernumber)
                print("ip[idx]:   ", ipblock_d.properties.ips[idx])
                ip = ipblock_d.properties.ips[idx]

                ipa=ip.split('.')
                ipa[3] = '1'
                ipgw = ".".join(ipa)
                print(ipgw)

    return ip,ipgw


# --------------------------------------------------------------------------
# Create NIC and attach it to the server (AFTER LAN!)
def nic_create(datacenter_id, lan_id, ifacename, server_id, host_config):
    print("Now creating nic ... lan_id: ", lan_id, ' server_id:', server_id,' iface:', ifacename)

    with ionoscloud.ApiClient(configuration) as api_client:
        nics_api = ionoscloud.NetworkInterfacesApi(api_client)
        
        if lan_id == host_config['public_lan_id']:
            nic_properties = ionoscloud.NicProperties(
                name=f"{host_config['name']}-public",
                lan=host_config['public_lan_id'],
                dhcp=True,
                ips=[host_config['public_ip']],
                firewall_active=False
            )

        if lan_id == host_config['private_lan_id']:
            nic_properties = ionoscloud.NicProperties(
                name=f"{host_config['name']}-public",
                lan=host_config['private_lan_id'],
                dhcp=True,
                firewall_active=False
            )

        nic = ionoscloud.Nic(properties=nic_properties)
        print('----------------- nic -------------------')
        print(nic)
        print('-----------------------------------------')
        time.sleep(15)

        try:
            print("\n3. Add network interface...")
            nic_response = nics_api.datacenters_servers_nics_post(
                datacenter_id=datacenter_id,
                server_id=server_id,
                nic=nic,
                depth=1
            )
            print(f"   ✓ NIC created: {nic_response.id}")
            
            # Wait for NIC to be ready
            print("   Waiting for NIC provisioning...")
            final_nic = wait_for_nic(api_client, datacenter_id, server_id, nic_response.id)
            
            print(f"   ✓ NIC ready: {final_nic.id}")
            print(f"   Name: {final_nic.properties.name}")
            print(f"   LAN: {final_nic.properties.lan}")
            print(f"   DHCP: {final_nic.properties.dhcp}")
            print(f"   IPs: {final_nic.properties.ips}")
            
        except ApiException as e:
            if e.status == 404 or e.code == 309:
                print("   2) NIC not yet available, please wait...")
            else:
                print(f'   ⚠ Error adding the NIC: {e}\n')
                raise

# --------------------------------------------------------------------------
# wait until NIC state is "AVAILABLE" (fully provisioned)
def wait_for_nic(api_client, datacenter_id, server_id, nic_id, timeout=300):
    nics_api = ionoscloud.NetworkInterfacesApi(api_client)
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            nic = nics_api.datacenters_servers_nics_find_by_id(
                datacenter_id=datacenter_id,
                server_id=server_id,
                nic_id=nic_id
            )
            state = nic.metadata.state
            print(f"   NIC Status: {state}")
            
            if state == "AVAILABLE":
                return nic
            elif state == "ERROR":
                raise Exception("NIC provisioning failed")
                
        except ApiException as e:
            # if e.status == 404 or e.code == 309:
            if e.status == 404:
                print("   NIC not available yet, please wait...")
            else:
                raise
                
        time.sleep(5)
    
    raise TimeoutError("NIC did not become available in time")

# --------------------------------------------------------------------------
# wait until LAN-state == AVAILABLE
def wait_for_lan(api_client, datacenter_id, lan_id, timeout=180):
    lans_api = ionoscloud.LANsApi(api_client)
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            lan = lans_api.datacenters_lans_find_by_id(
                datacenter_id=datacenter_id,
                lan_id=lan_id
            )
            state = lan.metadata.state
            print(f"   LAN Status: {state}")
            
            if state == "AVAILABLE":
                return lan
            elif state == "ERROR":
                raise Exception("LAN provisioning failed")
                
        except ApiException as e:
            if e.status == 404:
                print("   LAN not yet available, please wait...")
            else:
                raise
                
        time.sleep(5)
    
    raise TimeoutError("LAN did not become available in time")

# --------------------------------------------------------------------------
# create LAN with lan_id in datacenter_id (public or privat)
def lan_create(datacenter_id, lan_id, public, timeout=180):
    print("Starting lan_create ... datacenter: ",datacenter_id, "lan_id: ",lan_id)
    lan_id1 = lan_id

    with ionoscloud.ApiClient(configuration) as api_client:
        lans_api = ionoscloud.LANsApi(api_client)
        
        # Check whether LAN already exists
        if lan_id > 0:
            try:
                print(f"\n3a. Check existing LAN {lan_id}...")
                existing_lan = lans_api.datacenters_lans_find_by_id(
                    datacenter_id=datacenter_id,
                    lan_id=lan_id
                )
                print(f"   ✓ LAN {lan_id} already exists")
                print(f"   Name: {existing_lan.properties.name}")
                print(f"   Public: {existing_lan.properties.public}")
                
            except ApiException as e:
                if e.status == 404:
                    print(f"   ⚠ LAN {lan_id} Not found, create new LAN...")
                    lan_id = 0
                else:
                    print(f'   ✗ Error checking the LAN: {e}\n')
                    exit(1)
        
        # Create a new LAN if necessary
        if lan_id == 0:
            lan_properties = ionoscloud.LanProperties(
                name='server-lan'+str(lan_id1),
                public=public  # False für privates LAN, true for "public"
            )
            lan = ionoscloud.Lan(properties=lan_properties)
            
            try:
                print("\n3b. Create new LAN...")
                lan_response = lans_api.datacenters_lans_post(
                    datacenter_id=datacenter_id,
                    lan=lan,
                    depth=1
                )
                lan_id = lan_response.id
                print(f"   ✓ LAN created: {lan_id}")
                print(f"   Name: {lan_response.properties.name}")
                print(f"   Status: {lan_response.metadata.state}")
                
                # Waiting for LAN provisioning
                print("   Waiting for LAN provisioning ...")
                final_lan = wait_for_lan(api_client, datacenter_id, lan_id)
                print(f"   ✓ LAN ready!")
                
            except ApiException as e:
                print(f'   ✗ Error creating the LAN: {e}\n')
                exit(1)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

zservers = get_servers()
if zservers == 2:
    print (">>> now exit!")
    exit(1)

print("Create a server with Debian 12 boot volume")
print("lan_id: ",lan_id)
print("=" * 77)

# Init values
server_id = 0
volume_id = 0
public  = 'none'
private = 'none'
timestamp = datetime.now().strftime("%m%d-%H%M")  # Format: MMDD-HHMM
#
if servernumber == 1:
    # ssh-key create for server1/2 - only when servernumber == init !
    os.system('rm -frv .ssh_ons*')
    os.mkdir(".ssh_ons") 
    os.mkdir(".ssh_ons2") 
    os.system('ssh-keygen -t rsa -b 4096 -f .ssh_ons/id_rsa -N \"\"')
    os.system('ssh-keygen -t rsa -b 4096 -f .ssh_ons2/id_rsa -N \"\"')

# Read private / public key - ons
with open('.ssh_ons/id_rsa', 'rb') as f:
    private1 = base64.b64encode(f.read()).decode()
with open('.ssh_ons/id_rsa.pub', 'r') as f:
    public1 = f.read().strip()

# Read private / public key - ons2
with open('.ssh_ons2/id_rsa', 'rb') as f:
    private2 = base64.b64encode(f.read()).decode()
with open('.ssh_ons2/id_rsa.pub', 'r') as f:
    public2 = f.read().strip()

if servernumber == 1:
    public  = public1
    private = private1
    print("public1 private1 will be used!")

if servernumber == 2:
    public  = public2
    private = private2
    print("public2 private2 will be used!")

print("Keys encoded successfully!")
print(f"Private key (base64): {len(private)} chars")
print(f"Public1 key: {public1[:50]}...")
print(f"Public2 key: {public2[:50]}...")

ip_pub,ipgw = get_ip(servernumber)
h_name = 'opennebula-h'+str(servernumber)

h1_config = {
    'name': h_name,
    'ssh_public_key': public,
    'public_ip': ip_pub,
    'public_gateway': ipgw,
    'public_lan_id': lan_id,
    'private_lan_id': lan2_id
}
print("h1_config[h_name]",h1_config['name'])    
print("h1_config[ip_pub]",h1_config['public_ip'])    
print("h1_config[ipgw]",h1_config['public_gateway'])    

# Cloud-init script with f-string (IMPORTANT: f before """)
cloud_init_script = f"""#cloud-config
package_update: true
package_upgrade: true

packages:
  - git
  - vim
  - curl
  - wget
  - python3-pip
  - ansible
  - python3-venv
  - console-data

users:
  - name: root
    ssh_authorized_keys:
      - {public1}
      - {public2}

no_ssh_fingerprints: false
ssh:
  emit_keys_to_console: false

write_files:
  - path: /root/.ssh/id_rsa
    permissions: '0600'
    owner: root:root
    encoding: b64
    content: |
      {private}
  
  - path: /root/.ssh/id_rsa.pub
    permissions: '0644'
    owner: root:root
    content: |
      {public}
  
  - path: /etc/motd
    permissions: '0644'
    content: |
      ====================================
      Debian 12 server with pre-installed software
      Git, Hatch, Pipx, Ansible
      ====================================
  
  - path: /etc/sysctl.d/local.conf    
    permissions: '0644'
    owner: root:root
    content: |
      net.ipv4.ip_forward = 1

  - path: /root/server_info.txt
    permissions: '0644'
    content: |
      Server erstellt am: {timestamp}
      Datacenter: {datacenter_id}
      Volume: {volume_id}
      
  - path: /usr/local/bin/setup_status.sh
    permissions: '0755'
    owner: root:root
    content: |
      #!/bin/bash
      echo "Cloud-Init Status:"
      cloud-init status --long
      echo ""
      echo "Installation Log:"
      cat /root/install.log

runcmd:
  - pip3 install --break-system-packages hatch pipx
  - pipx ensurepath
  - chmod 600 /root/.ssh/id_rsa
  - chmod 644 /root/.ssh/id_rsa.pub
  - echo "Installation abgeschlossen" > /root/install.log
  - systemctl restart ssh      
  - ssh-keygen -A
"""

# *** BASE64-ENKODIERUNG - WICHTIG! ***
cloud_init_encoded = base64.b64encode(cloud_init_script.encode('utf-8')).decode('utf-8')

print("=" * 77)
print("Cloud-Init Skript (Base64-encoded):")
print(cloud_init_encoded[:100] + "...")  # show 100 characters
print("=" * 77)
#
Cloud_Init_logfile = 'Cloud-Init'+str(servernumber)+'.log'
print("writing Cloud-Init Skript into file: ", Cloud_Init_logfile)
with open(Cloud_Init_logfile, 'w') as f:
    f.write(cloud_init_script)
#
#
#
#
#################################################################
# Step 1: Create volume with Debian 12 image

with ionoscloud.ApiClient(configuration) as api_client:
    volumes_api = ionoscloud.VolumesApi(api_client)
    volume_id=0

    name = 'deb12-boot-'+str(servernumber)
    # Define volume properties
    volume_properties = ionoscloud.VolumeProperties(
        name=name, 
        size=h_disk_size,
        type='HDD',
        image_alias= 'debian:12',
        image_password=h_passw, # Root-Password (mindestens 8 char)
        boot_order='PRIMARY', # or NONE or AUTO
        # ssh_keys=['ssh-rsa AAAAB3NzaC1yc2EAAA...']  # Optional: SSH Public Keys
        user_data=cloud_init_encoded,  # ← Cloud-Init Skript!
        availability_zone='AUTO'  # AUTO, ZONE_1, ZONE_2, oder ZONE_3
    )
    volume = ionoscloud.Volume(properties=volume_properties)
    
    try:
        print("\n1. Create boot volume with Debian 12...")
        volume_response = volumes_api.datacenters_volumes_post(
            datacenter_id=datacenter_id,
            volume=volume,
            pretty=True,
            depth=1
        )
        volume_id = volume_response.id
        print(f"   ✓ Volume erstellt: {volume_id}")
        print(f"   Name: {volume_response.properties.name}")
        print(f"   Größe: {volume_response.properties.size} GB")
        print(f"   Typ: {volume_response.properties.type}")
        print(f"   Image: {volume_response.properties.image}")
        print(f"   Status: {volume_response.metadata.state}")
        print(f"   Cloud-Init: Aktiviert")

    except ApiException as e:
        print(f'   ✗ 1) Error creating volume: {e}\n')
        exit(1)

    # Waiting for volume provisioning
    print("\n   Waiting for volume provisioning...")
    timeout = 120  # seconds
    start_time = time.time()

    time.sleep(60)
    print("2) Status: ", volume_response.metadata.state)

    volume_status = volumes_api.datacenters_volumes_find_by_id(
        datacenter_id=datacenter_id,
        volume_id=volume_id,
        depth=1
    )
    print("3) Status: ", volume_status.metadata.state)

    if volume_status.metadata.state == 'AVAILABLE':
        print(f"   ✓ Volume is ready!")
    else:
        time.sleep(30)

#################################################################
# Step 2: Create a server with this volume as the boot volume

with ionoscloud.ApiClient(configuration) as api_client:
    servers_api = ionoscloud.ServersApi(api_client)
    
    # Define server properties
    server_properties = ionoscloud.ServerProperties(
        name=h_name,
        cores=h_cores,
        ram=h_ram,   
        availability_zone='AUTO',
        cpu_family='INTEL_SKYLAKE', # INTEL_SKYLAKE, AMD_OPTERON, INTEL_XEON
        type='ENTERPRISE'           # ENTERPRISE oder CUBE
    )
    
    # Create a server with an attached volume
    server_entities = ionoscloud.ServerEntities(
        volumes=ionoscloud.AttachedVolumes(
            items=[
                ionoscloud.Volume(id=volume_id)
            ]
        )
    )

    server = ionoscloud.Server(
        properties=server_properties,
        entities=server_entities
    )

    try:
        print("\n2. Create server and attach volume ...")
        server_response = servers_api.datacenters_servers_post(
            datacenter_id=datacenter_id,
            server=server,
            pretty=True,
            depth=2
        )
        
        server_id = server_response.id
        print(f"   ✓ Server created: {server_id}")
        print(f"   Name: {server_response.properties.name}")
        print(f"   Cores: {server_response.properties.cores}")
        print(f"   RAM: {server_response.properties.ram} MB")
        print(f"   Status: {server_response.metadata.state}")
        print('-----------------------------')

        # Zeige angehängte Volumes
        if server_response.entities and server_response.entities.volumes:
            print(f"\n   Attached volumes:")
            for vol in server_response.entities.volumes.items:
                print(f"     id: ({vol.id})")
        
    except ApiException as e:
        print(f'   ✗ Error creating server: {e}\n')
        exit(1)


#####################################################
# After creating the server, wait and then set the boot volume.:
with ionoscloud.ApiClient(configuration) as api_client:
    servers_api = ionoscloud.ServersApi(api_client)
    volumes_api = ionoscloud.VolumesApi(api_client)
    
    # Waiting for server provisioning
    print("\n       # Waiting for server provisioning ...")
    timeout = 300
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            server_status = servers_api.datacenters_servers_find_by_id(
                datacenter_id=datacenter_id,
                server_id=server_id,
                depth=1
            )
            state = server_status.metadata.state
            print(f"   Server Status: {state}")
            
            if state == "AVAILABLE":
                print(f"   ✓ Server is ready!")
                break
            elif state == "ERROR":
                raise Exception("Server provisioning failed")
                
        except ApiException as e:
            if e.status == 404:
                print("   Server not available yet, please wait ...")
            else:
                raise
                
        time.sleep(5)
    

#####################################################
# Set boot volume explicitly
    try:
        print(f"\n   Set boot volume ... server_id: {server_id} - volume_id: {volume_id}")
        # update Server-Properties 
        server_update = ionoscloud.ServerProperties(
            boot_volume=ionoscloud.ResourceReference(id=volume_id)
        )
        
        server_response = servers_api.datacenters_servers_patch(
            datacenter_id=datacenter_id,
            server_id=server_id,
            server=server_update,
            depth=1
        )

        print(f"   ✓ Boot volume set: {volume_id}")
        
    except ApiException as e:
        print(f'   ⚠ Error setting the boot volume: {e}\n')


#################################################################
# Step 3: Create or check LAN (BEFORE NIC attachment!)
lan_create(datacenter_id, lan_id, 'True', timeout=180)

#################################################################
# Step 4: Create NIC and attach it to the server (AFTER LAN!)
# h1_config - see above (network-config values from .env)

nic_create(datacenter_id, lan_id,  'eth0', server_id, h1_config)
nic_create(datacenter_id, lan2_id, 'eth1', server_id, h1_config)


# end, write some info
print("\n" + "=" * 77)
print("✓ Server creation complete!")
print("=" * 77)
print(f"\nServer-ID: {server_id}")
print(f"Volume-ID: {volume_id}")
print("\naccess:")
print(f"  - SSH: ssh root@<server-ip>")
print(f"  - password: MySecure!Password2024")
print("\nNote: Server starts automatically.")
print("=" * 77)
#
#

