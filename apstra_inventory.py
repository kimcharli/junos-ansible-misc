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

            self.inventory['_meta']['hostvars'][name] = { 'ansible_host': mgmt_ipaddr }
            self.inventory['all']['children'].append(hw_model)
            if hw_model not in self.inventory:
                self.inventory[hw_model] = { 'hosts': [] }
            self.inventory[hw_model]['hosts'].append(name)

        return

        return {

            # results of inventory script as above go here
            # ...
            # "group001": {
            #     "hosts": ["host001", "host002"],
            #     "vars": {
            #         "var1": true
            #     },
            #     "children": ["group002"]
            # },
            "all": {
                "children": [
                    "ungrouped",
                    "ex4300"
                ]
            },            
            "ex4300": {
                "hosts": ["host001","host002"],
                "vars": {
                    "var2": 500
                },
                "children":[]
            },
            "_meta": {
                "hostvars": {
                    "host001": {
                        "ansible_host" : "192.168.210.27"
                    },
                    "host002": {
                        "ansible_host": "192.168.210.30"
                    }
                }
            }
        }

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

