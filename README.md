# junos-ansible-misc

## setup

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

ansible-galaxy collection install junipernetworks.junos

```

## run

Edit hosts.ini

```
ansible-playbook pb.check-firmware.yaml
```

