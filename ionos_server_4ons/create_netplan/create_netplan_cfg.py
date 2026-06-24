#!/home/pydev/.venv/bin/python
#
from __future__ import print_function
import time
import ionoscloud
from ionoscloud.rest import ApiException
# from ruamel.yaml import YAML
import ruamel.yaml

import os

# Defining the host is optional and defaults to https://api.ionos.com/cloudapi/v6
configuration = ionoscloud.Configuration(
    host = 'https://api.ionos.com/cloudapi/v6',
)

from dotenv import dotenv_values
config = {
    **dotenv_values(".env"),  # load shared development variables
}

datacenter_id          = config['dc_id']
configuration.token    = config['token']

print('---------------------------')
print("-------  datacenter_id") 
print(datacenter_id) 

# --------------------------------------------------------------------------
def yaml_replace2(ip_host, hname, ip_priv, ipgw):

    yaml = ruamel.yaml.YAML()
    yaml.indent(sequence=4, offset=2)
    yaml.preserve_quotes = True
    yaml.explicit_start = True

    output_file = hname+".yaml"
    print(">>> hname:",hname," -- output_file",output_file)
    if hname  == "h1":
        print(">>> hname:",hname," -- 2nd output_file","fe.yaml")

    try:
        with open('_netplan_templates/h1.yaml') as stream:
            data = yaml.load(stream)

    except Exception as e:
        print(f'   ✗ error opening inventory-file: {e}\n')
        print ("Error:",e.errno)
        return e.errno

    d_br0 = data["network"]["bridges"]
    addresses_list = d_br0["br0"]["addresses"]
    addresses_list[0] = ip_host+"/32"
    addresses_list[1] = ip_priv+"/32"
    
    d_br0["br0"].update(dict(addresses=addresses_list))
    print("-" * 50)
    ipgw32 = ipgw+"/32"
    d_br0["br0"]["routes"][0].update(dict(to=ipgw32 ))
    d_br0["br0"]["routes"][1].update(dict(via=ipgw ))

    with open(output_file, 'wb') as stream:
        yaml.dump(data, stream)

    if hname  == "h1":
        with open('fe.yaml', 'wb') as stream:
            yaml.dump(data, stream)

    return 0

# --------------------------------------------------------------------------
# get gateway or network_address from ip
def gw_nw_get(gw_nw,ip,gw_name):

    ipa=ip.split('.')
    ipa[3] = gw_nw   # '1'
    ipg_new = ".".join(ipa)
    return ipg_new
# --------------------------------------------------------------------------


with ionoscloud.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = ionoscloud.ServersApi(api_client)
    # datacenter_id = 'datacenter_id_example' # str | The unique ID of the data center.
    try:
        # List servers 
        servers = api_instance.datacenters_servers_get(datacenter_id, depth=1)
        ipz  = 0
        ip_dict = {}
        ip_lan  = {}
        sname_dict = {}
        for server in servers.items:
            print("server info:", "-" * 34)
            print(f"  └─ NAME: {server.properties.name}")
            print(f"     ├─ ID: {server.id}")
            print(f"     ├─ CREATED: {server.metadata.created_date}")
            print(f"     ├─ STATE: {server.metadata.state}")
            print(f"     ├─ VM_STATE: {server.properties.vm_state}")
            sname = server.properties.name

            with ionoscloud.ApiClient(configuration) as api_client:
                    # Create an instance of the API class
                    api_instance = ionoscloud.NetworkInterfacesApi(api_client)
                    # 'datacenter_id' # str | The unique ID of the data center.
                    # 'server.id'     # str | The unique ID of the server.
                    depth = 3
                    try:
                        # List NICs
                        api_response = api_instance.datacenters_servers_nics_get(datacenter_id, server.id)
                        nics_per_server = 1

                        for nic in api_response.items:
                            nic_id = nic.id
                            try:
                                # Retrieve NICs
                                nic2 = api_instance.datacenters_servers_nics_find_by_id(datacenter_id, server.id, nic_id)
                                ip_dict[ipz] = nic2.properties.ips
                                ip_lan[ipz] = nic2.properties.lan
                                sname_dict[ipz] = server.properties.name
                                ipz  = ipz  +1

                            except ApiException as e:
                                print('Exception when calling NetworkInterfacesApi.datacenters_servers_nics_find_by_id: %s\n' % e)

                            nics_per_server = nics_per_server +1

                    except ApiException as e:
                        print('Exception when calling NetworkInterfacesApi.datacenters_servers_nics_get: %s\n' % e)

    except ApiException as e:
        print('Exception when calling ServersApi.datacenters_servers_get: %s\n' % e)

    print("-" * 50)
    for key, value in ip_dict.items():

        if sname_dict[key] == 'opennebula-h1' and ip_lan[key] == 1:
            ip_h1    = value[0]
            print(f"{'ip_h1':<10} {ip_h1:<17}")
            ip_fe = ip_h1   
            print(f"{'ip_fe':<10} {ip_fe:<17}")  # h1 and fe (frontend) == same server

        if sname_dict[key] == 'opennebula-h1' and ip_lan[key] == 2:
            ip_priv1 = value[0]
            print(f"{'ip_priv1':<10} {ip_priv1:<17}")

        if sname_dict[key] == 'opennebula-h2' and ip_lan[key] == 1:
            ip_h2    = value[0]
            print(f"{'ip_h2':<10} {ip_h2:<17}")

        if sname_dict[key] == 'opennebula-h2' and ip_lan[key] == 2:
            ip_priv2 = value[0]
            print(f"{'ip_priv2':<10} {ip_priv2:<17}")

    print("-" * 50)
#
# 
ipgw1    = gw_nw_get('1', ip_h1,'ipgw1')
ipgw2    = gw_nw_get('1', ip_h2,'ipgw2')

nw_priv1 = gw_nw_get('0', ip_priv1,'nw_priv1')

#
rc = yaml_replace2(ip_h1, "h1", ip_priv1, ipgw1)
#
rc = yaml_replace2(ip_h2, "h2", ip_priv2, ipgw2)
#


