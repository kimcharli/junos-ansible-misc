# junos-ansible-misc

## setup

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

ansible-galaxy collection install junipernetworks.junos

```

## run

Edit hosts.ini

```
ansible-playbook pb.check-firmware.yaml
```

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
```