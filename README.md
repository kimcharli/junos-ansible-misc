# junos-ansible-misc

## setup

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

ansible-galaxy collection install junipernetworks.junos

```

## run with hosts file

Edit hosts.ini

```
ansible-playbook pb.check-firmware.yaml

ansible-playbook pb.check-firmware.yaml
```

## run with dynamic inventory
For Apstra, edit .env
```
apstra_server_host=192.168.210.15
apstra_server_password=securepassword
apstra_server_port=443
apstra_server_username=admin
ansible_user=admin
ansible_ssh_pass=securepassword  
```


```
ansible-playbook  -i apstra_inventory.py pb.check-firmware.yaml

ansible-playbook  -i apstra_inventory.py pb.check-firmware.yaml
```


## inventory operations
```
(venv) ckim@ckim-mbp:junos-ansible-misc % ansible-inventory --inventory apstra_inventory.py --host LEAF05-192.168.0.205
[WARNING]: Invalid characters were found in group names but not replaced, use -vvvv to see details
{
    "ansible_connection": "network_cli",
    "ansible_host": "192.168.0.205",
    "ansible_network_os": "junipernetworks.junos.junos",
    "ansible_ssh_pass": "XXXXXXX",
    "ansible_user": "ckim",
    "junso_hw_model": "QFX5220-128C",
    "junso_hw_version": "REV 12",
    "junso_os_version": "22.2R3-S2.5-EVO"
}
```
