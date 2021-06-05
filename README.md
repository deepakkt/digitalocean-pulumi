### Spinning up loadbalanced droplets

This example will spin up one or more droplets with Pulumi on DigitalOcean.
The loadbalancer will not be created if there is only one droplet chosen.

![Architecture](https://github.com/deepakkt/digitalocean-pulumi/blob/main/images/img.png?raw=true)

#### Common Pre-requisites

* Of course, you will need an account with DO
* Create a token with required permissions on DO
* Create a Pulumi account and authenticate with Pulumi using the CLI. [Read the documentation on Pulumi](https://www.pulumi.com/docs/reference/cli/pulumi_login/) on how to do this
* Create SSH keys on DO to pre-activate passwordless login
* If needed, setup a subdomain on Digitalocean. You may need to point the Nameserver of your domain provider to DO (That is beyond the scope of this sample)

#### Running locally

* Create an env var for Pulumi to authenticate to DigitalOcean. It must be named `DIGITALOCEAN_TOKEN`
* Create a Python virtual environment
* Activate the environment and `pip install -r requirements.txt`

#### Running on Jenkins

* Setup a Jenkins project
* Use the `Jenkinsfile_spinup` and `Jenkinsfile_teardown`
* This runs the entire suite on Docker
* Set required env vars on the Jenkins project

#### Configurations

* SSH Keys
* Project name
* Domain name
* Number of droplets
* Region, image, droplet size

