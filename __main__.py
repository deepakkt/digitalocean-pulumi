from pprint import pprint

import pulumi
import pulumi_digitalocean as do
from pulumi import export

droplet_count = 1
region = "blr1"

stack_name = pulumi.get_stack()
project_name = "aasaan-dev-{}".format(stack_name)

regions = do.get_regions()
domain_name = "{}.aasaan.do.ktdpack.com".format(stack_name)

user_data = """#!/bin/bash
  sudo apt-get update
  sudo apt-get install -y nginx
"""

# regions = do.get_regions()
# print(["{} - {}".format(x.slug, x.name) for x in regions.regions])

ssh_key = do.get_ssh_key("aasaan-jenkins")

# images = do.get_images()
# for x in images.images:
#     if "blr1" in x.regions:
#         print(x.description, x.slug)
# print([x.description for x in images.images if "blr1" in x.regions])

# project = do.get_project(name="aasaan")
# print("found project ==> ", project.id, project.name, project.description)

droplet_type_tag = do.Tag("aasaan")

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
        ssh_keys=[ssh_key.fingerprint],
    )

# loadbalancer = do.LoadBalancer(
#     "public",
#     droplet_tag=droplet_type_tag.name,
#     forwarding_rules=[do.LoadBalancerForwardingRuleArgs(
#         entry_port=80,
#         entry_protocol="http",
#         target_port=80,
#         target_protocol="http",
#     )],
#     healthcheck=do.LoadBalancerHealthcheckArgs(
#         port=80,
#         protocol="tcp",
#     ),
#     region=region,
# )

domain = do.Domain(
    "do-domain",
    name=domain_name,
    ip_address=droplet.ipv4_address,
)

target = do.Project(
    "aasaan-dev",
    name=project_name,
    resources=[
        droplet.droplet_urn,
        domain.domain_urn,
    ]
)

# export("endpoint", loadbalancer.ip)
export("droplet", droplet.ipv4_address)
export("droplet urn", droplet.droplet_urn)
