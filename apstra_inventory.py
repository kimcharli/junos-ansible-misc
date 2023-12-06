#!/usr/bin/env python
# chmod +x apstra-inventory.py
# ./apstra_inventory.py --list  
# ansible-inventory --inventory apstra_invetory.py --list
# 
# .env file example
# apstra_server_host=10.85.192.54
# apstra_server_password=zaq1@WSXcde3$RFV
# apstra_server_port=443
# apstra_server_username=admin
# ansible_user=admin
# ansible_ssh_pass=zaq1@WSXcde3$RFV


from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
import json
import sys
import argparse
import os
from dotenv import load_dotenv
import urllib3
import requests


class CkApstra():
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.session = requests.Session()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.session.verify = False
        self.session.headers.update({'Content-Type': "application/json"})
        self.url_prefix = f"https://{self.host}:{self.port}/api"
        self.login()

    def login(self) -> None:
        """
        Log in to the Apstra controller.
        """
        url = f"{self.url_prefix}/user/login"
        payload = {
            "username": self.username,
            "password": self.password
        }
        response = self.session.post(url, json=payload)
        # print(f"{response.content=}")
        self.token = response.json()["token"]
        self.session.headers.update({'AuthToken': self.token})

    def get_items(self, url: str) -> dict:
        """
        Get the items from the url.

        Args:
            The url under /api

        Returns:
            The items
        """
        url = f"{self.url_prefix}/{url}"
        # self.logger.debug(f"{url=}")
        return self.session.get(url).json()


class ApstrInventory():
    def __init__(self, apsrta_session):
        self.apstra_session = apsrta_session
        self.inventory = {
            "all": {
                "children": [],
                "vars": {
                    "ansible_user": "admin",
                    "ansible_ssh_pass": "password",
                    "ansible_connection": "ansible.netcommon.netconf",
                    "ansible_network_os": "junipernetworks.junos.junos",
                    "ansible_connection": "network_cli",
                },
            },            
            # "ex4300": {
            #     "hosts": ["host001","host002"],
            #     "vars": {
            #         "var2": 500
            #     },
            #     "children":[]
            # },
            "_meta": {
                "hostvars": {
                    # "host001": {
                    #     "ansible_host" : "192.168.210.27"
                    # },
                    # "host002": {
                    #     "ansible_host": "192.168.210.30"
                    # }
                }
            }
        }

        self.inventory['all']['vars']['ansible_user'] = os.getenv('ansible_user')
        self.inventory['all']['vars']['ansible_ssh_pass'] = os.getenv('ansible_ssh_pass')

        parser = argparse.ArgumentParser()
        parser.add_argument('--list', help='list', action='store_true')
        parser.add_argument('--host', help='host')
        args = parser.parse_args()

                
        # Called with `--list`.
        if args.list:
            self.apstra_inventory()
        # Called with `--host [hostname]`.
        elif self.args.host:
            # Not implemented, since we return _meta info `--list`.
            self.inventory = self.empty_inventory()
        # If no groups or vars are present, return an empty inventory.
        else:
            self.inventory = self.empty_inventory()

        print(json.dumps(self.inventory))   


    def apstra_inventory(self):
        systems = self.apstra_session.get_items("systems")
        # print(f"{systems['items'][0]=}")

        a_system_example = {
            'container_status': {'error': '', 'host': 'AosController', 'name': 'aos-offbox-192_168_210_104-f', 'status': 'running'}, 
            'device_key': 'XR3622090624', 
            'facts': {'aos_hcl_model': 'Juniper_EX4300-48MP_Junos', 'aos_server': '192.168.210.15', 'aos_version': 'AOS_4.1.2.5_OB.4', 
                    'chassis_mac_ranges': '4c:73:4f:53:4e:bc-4c:73:4f:53:53:bb', 'hw_model': 'EX4300-48MP', 'hw_version': 'REV 11', 
                    'mgmt_ifname': 'vme', 'mgmt_ipaddr': '192.168.210.104', 'mgmt_macaddr': '4C:73:4F:53:4E:BD', 
                    'os_arch': 'x86_64', 'os_family': 'Junos', 'os_version': '22.4R2-S2.6', 
                    'os_version_info': {'build': '6', 'major': '22', 'minor': '4R2-S2'}, 
                    'serial_number': 'XR3622090624', 'vendor': 'Juniper'}, 
            'id': 'XR3622090624', 
            'status': {'agent_start_time': '2023-11-12T14:16:03.671994Z', 'blueprint_active': True, 'blueprint_id': '8de650e3-56e5-4f87-86d7-b177ad0be58f', 
                    'comm_state': 'on', 'device_start_time': '2023-10-19T11:35:14.000000Z', 'domain_name': '', 'error_message': '', 'fqdn': 'BPN-NETSW-4202-104', 
                    'hostname': 'BPN-NETSW-4202-104', 'is_acknowledged': True, 'operation_mode': 'full_control', 'pool_id': 'default_pool', 'state': 'IS-ACTIVE'}, 
            'user_config': {'admin_state': 'normal', 'aos_hcl_model': 'Juniper_EX4300-48MP_Junos', 'location': ''}
        }

        for system in systems['items']:
            if system['container_status']['status'] != 'running':
                continue
            hostname = f"{system['status']['hostname']}"
            device_key = system['device_key']
            hw_model = system['facts']['hw_model']
            hw_version = system['facts']['hw_version']
            mgmt_ipaddr = system['facts']['mgmt_ipaddr']
            os_version = system['facts']['os_version']
            name=f"{hostname}-{mgmt_ipaddr}"

            self.inventory['_meta']['hostvars'][name] = { 'ansible_host': mgmt_ipaddr, "junso_hw_model": hw_model, "junso_hw_version": hw_version, "junso_os_version": os_version }

            if hw_model not in self.inventory['all']['children']:
                self.inventory['all']['children'].append(hw_model)
            if hw_model not in self.inventory:
                self.inventory[hw_model] = { 'hosts': [] }
            self.inventory[hw_model]['hosts'].append(name)

        return


if __name__ == '__main__':
    load_dotenv()
    apstra_server_host = os.getenv('apstra_server_host')
    apstra_server_port = os.getenv('apstra_server_port')
    apstra_server_username = os.getenv('apstra_server_username')
    apstra_server_password = os.getenv('apstra_server_password')
    session = CkApstra(
        apstra_server_host, 
        apstra_server_port,
        apstra_server_username,
        apstra_server_password,
        )
    inv = ApstrInventory(session)

