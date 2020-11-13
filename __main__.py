import os

import pulumi
import pulumi_digitalocean as do
from pulumi import export


def get_ssh_keys(keys_list):
    return map(do.get_ssh_key, keys_list)

def get_envs():
    return {
        "DROPLET_COUNT": int(os.getenv("DROPLET_COUNT", "1")),
        "BASE_DOMAIN": os.getenv("BASE_DOMAIN") or "aasaan.do.ktdpack.com",
        "PROJECT_BASE_NAME": os.getenv("PROJECT_BASE_NAME") or "aasaan-dev",
        "DO_REGION": os.getenv("DO_REGION") or "blr1",
        "VPS_TYPE": os.getenv("VPS_TYPE") or "s-1vcpu-1gb",
        "VPS_IMAGE": os.getenv("VPS_IMAGE") or "docker-20-04",
    }


env_settings = get_envs()

droplet_count = env_settings.get("DROPLET_COUNT", 1)
region = env_settings.get("DO_REGION", "blr1")
project_base_name = env_settings.get("PROJECT_BASE_NAME", "aasaan-dev")
base_domain = env_settings.get("BASE_DOMAIN", "aasaan.do.ktdpack.com")

stack_name = pulumi.get_stack()
project_name = "{}-{}".format(project_base_name, stack_name)

loadbalancer = ""

user_data = """#!/bin/bash
  sudo apt-get update
  sudo apt-get install -y nginx
"""


key_list = [
    "digitalocean-ipc-droplet",
    "asus",
    "aasaan-jenkins",
]
ssh_keys=[ssh_key.fingerprint for ssh_key in get_ssh_keys(key_list)]


droplet_type_tag = do.Tag("aasaan")
droplets = []
domain_names = dict()

for x in range(1, droplet_count + 1):
    instance_name = "web-%s" %x
    name_tag = do.Tag(instance_name)
    droplet = do.Droplet(
        instance_name,
        image="docker-20-04",
        region=region,
        size="s-1vcpu-1gb",
        tags=[name_tag.id, droplet_type_tag.id],
        user_data=user_data,
        ssh_keys=ssh_keys,
    )
    droplets.append(droplet)
    domain_names["{}{}".format(stack_name, x)] = droplet.ipv4_address

if droplet_count > 1:
    loadbalancer = do.LoadBalancer(
        "{}-lb".format(project_base_name),
        droplet_tag=droplet_type_tag.name,
        forwarding_rules=[do.LoadBalancerForwardingRuleArgs(
            entry_port=80,
            entry_protocol="http",
            target_port=80,
            target_protocol="http",
        )],
        healthcheck=do.LoadBalancerHealthcheckArgs(
            port=80,
            protocol="tcp",
        ),
        region=region,
    )
    domain_names["{}".format(stack_name)] = loadbalancer.ip

domains = []
for each_domain in domain_names:
    domain = do.Domain(
        each_domain,
        name="{}.{}".format(each_domain, base_domain),
        ip_address=domain_names[each_domain]
    )
    domains.append(domain)

urns = [d.droplet_urn for d in droplets] + [d.domain_urn for d in domains]
if loadbalancer:
    urns.append(loadbalancer.load_balancer_urn)

target = do.Project(
    project_base_name,
    name=project_name,
    resources=urns
)

if loadbalancer:
    export("endpoint", loadbalancer.ip)

for droplet in droplets:
    export("droplet", droplet.ipv4_address)

for domain in domains:
    export("domain", domain.name)
