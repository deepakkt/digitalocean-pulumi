import os

import pulumi
import pulumi_digitalocean as do
from pulumi import export


def get_ssh_keys(keys_list):
    return map(do.get_ssh_key, keys_list)

droplet_count = int(os.getenv("DROPLET_COUNT"))
region = "blr1"

stack_name = pulumi.get_stack()
project_name = "aasaan-dev-{}".format(stack_name)

regions = do.get_regions()
domain_name = "{}.aasaan.do.ktdpack.com".format(stack_name)
loadbalancer = ""

user_data = """#!/bin/bash
  sudo apt-get update
  sudo apt-get install -y nginx
"""

# regions = do.get_regions()
# print(["{} - {}".format(x.slug, x.name) for x in regions.regions])

key_list = [
    "digitalocean-ipc-droplet",
    "asus",
    "aasaan-jenkins",
]

# images = do.get_images()
# for x in images.images:
#     if "blr1" in x.regions:
#         print(x.description, x.slug)
# print([x.description for x in images.images if "blr1" in x.regions])

# project = do.get_project(name="aasaan")
# print("found project ==> ", project.id, project.name, project.description)

droplet_type_tag = do.Tag("aasaan")
droplets = []

for x in range(0, droplet_count):
    instance_name = "web-%s" %x
    name_tag = do.Tag(instance_name)
    droplet = do.Droplet(
        instance_name,
        image="docker-20-04",
        region=region,
        size="s-1vcpu-1gb",
        tags=[name_tag.id, droplet_type_tag.id],
        user_data=user_data,
        ssh_keys=[ssh_key.fingerprint for ssh_key in get_ssh_keys(key_list)],
    )
    droplets.append(droplet)

if droplet_count > 1:
    loadbalancer = do.LoadBalancer(
        "public",
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

ipv4_address = loadbalancer.ip if loadbalancer else droplet.ipv4_address

domain = do.Domain(
    "do-domain",
    name=domain_name,
    ip_address=ipv4_address,
)

urns = [d.droplet_urn for d in droplets] + [domain.domain_urn]
if loadbalancer:
    urns.append(loadbalancer.load_balancer_urn)

target = do.Project(
    "aasaan-dev",
    name=project_name,
    resources=urns
)

if loadbalancer:
    export("endpoint", loadbalancer.ip)
export("droplet", droplet.ipv4_address)
export("domain", domain.name)
