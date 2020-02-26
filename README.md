# omaha-server

[![Build Status](https://travis-ci.com/dentalwings/omaha-server.svg?branch=master)](https://travis-ci.com/dentalwings/omaha-server)
[![Coverage Status](https://coveralls.io/repos/github/dentalwings/omaha-server/badge.svg?branch=travis-tests)](https://coveralls.io/github/dentalwings/omaha-server?branch=travis-tests)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/dentalwings/omaha-server/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/dentalwings/omaha-server/?branch=master)
[![Apache License, Version 2.0](https://img.shields.io/badge/license-Apache%202.0-red.svg)](https://github.com/dentalwings/omaha-server/blob/master/LICENSE)

**Omaha server no longer supports Python version 2 and Django 1.11 or lower version. If you need the old version of the application, then check the old_master branch.**

Google Omaha server implementation and Sparkle (mac) feed management.

Currently, Crystalnix's implementation is integrated into the updating processes of several organizations for products that require sophisticated update logic and advanced usage statistics. Crystalnix provide additional support and further enhancement on a contract basis. For a case study and enquiries please refer to [Crystalnix website](https://www.crystalnix.com/case-study/google-omaha)

## Setting up a development environment at AWS Cloud9

### Cloud9 environment creation

* Open the [AWS Cloud9 Console](https://ca-central-1.console.aws.amazon.com/cloud9/home?region=ca-central-1)
  * Create an environment and give it a name which identify you as the owner.
    > Cloud9 IDE environment can be shared with others for pair programming, but it is bound to your account and personalized to you!
  * Use the following environment settings:
    * Environment type: Create a new instance for environment (EC2)
    * Instance type: t2.micro (1 GiB RAM + 1 vCPU)
    * Platform: Ubuntu Server 18.04 LTS
    * Network settings (advanced): select the same VPC and one subnet you [EKS cluster](https://ca-central-1.console.aws.amazon.com/eks/home?region=ca-central-1#/clusters) use

### Cloud9 environment configuration

* install tools
  ```shell
  # update pip3 and pipenv
  sudo pip3 install --upgrade pip
  pip3 install pipenv
  
  # docker-compose
  sudo curl -L "https://github.com/docker/compose/releases/download/1.25.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  sudo curl -L https://raw.githubusercontent.com/docker/compose/1.25.3/contrib/completion/bash/docker-compose -o /etc/bash_completion.d/docker-compose
  
  # kubernetes
  sudo snap install kubectl --classic
  source <(kubectl completion bash)
  echo "source <(kubectl completion bash)" >> ~/.bashrc
  
  # aws cli auto completion
  echo "complete -C '/usr/local/bin/aws_completer' aws" >> ~/.bashrc
  ```
* Generate an ssh key (please set a passphrase!)
  ```shell
  ssh-keygen
  ```
* add your public key to your [GitHub account](https://github.com/settings/keys)
  ```shell
  cat ~/.ssh/id_rsa.pub
  ```
* Configure your git user and editor settings:
  ```shell
  git config --global user.name "Your Name"
  git config --global user.email you@example.com
  # fix cloud9 git editor bug on Ubuntu host
  sudo ln -s /bin/nano /usr/bin/nano
  ```
* Clone this repository and change working directory
  ```shell
  git clone git@github.com:dentalwings/omaha-server.git
  cd omaha-server
  
  # checkout the appropiate branch, e.g.:
  git checkout python3.6
  ```
* Install python project specific modules
  ```shell
  pipenv install --system --dev
  ```
* Click on `AWS Cloud9`in the menu -> `Open Your Project Settings` and replace the `run` section with the following code block
  > Cloud9 may be overwrite your changes, so maybe you should hard reload the IDE (CRTL+SHIFT+R in Chrome) after saving the file. Repeat this step if its not working the first time.
  ```javascript
  "run": {
        "configs": {
            "@inited": true,
            "json()": {
                "OmahaServer create admin": {
                    "command": "omaha-server/omaha_server/createadmin.py",
                    "cwd": "/omaha-server/omaha_server",
                    "debug": false,
                    "env": {
                        "DJANGO_SETTINGS_MODULE": "omaha_server.settings_cloud9",
                        "OMAHA_SERVER_PRIVATE": "True"
                    },
                    "name": "OmahaServer createadmin",
                    "runner": "Python 3",
                    "toolbar": true
                },
                "OmahaServer migrate": {
                    "command": "omaha-server/omaha_server/manage.py migrate",
                    "cwd": "/omaha-server/omaha_server",
                    "debug": false,
                    "env": {
                        "DJANGO_SETTINGS_MODULE": "omaha_server.settings_cloud9",
                        "OMAHA_SERVER_PRIVATE": "True"
                    },
                    "name": "OmahaServer migrate",
                    "runner": "Python 3",
                    "toolbar": true
                },
                "OmahaServer run server": {
                    "command": "omaha-server/omaha_server/manage.py runserver 8080",
                    "cwd": "/omaha-server/omaha_server",
                    "debug": true,
                    "env": {
                        "DJANGO_SETTINGS_MODULE": "omaha_server.settings_cloud9",
                        "OMAHA_SERVER_PRIVATE": "True"
                    },
                    "name": "OmahaServer run server",
                    "runner": "Python 3",
                    "toolbar": true
                },
                "OmahaServer test private": {
                    "command": "omaha-server/omaha_server/manage.py test -v 2",
                    "cwd": "/omaha-server/omaha_server",
                    "debug": false,
                    "env": {
                        "OMAHA_SERVER_PRIVATE": "True"
                    },
                    "name": "OmahaServer test private",
                    "runner": "Python 3",
                    "toolbar": true
                },
                "OmahaServer test private db": {
                    "command": "omaha-server/omaha_server/manage.py test -v 2",
                    "cwd": "/omaha-server/omaha_server",
                    "debug": false,
                    "env": {
                        "DJANGO_SETTINGS_MODULE": "omaha_server.settings_test_postgres",
                        "OMAHA_SERVER_PRIVATE": "True"
                    },
                    "name": "OmahaServer test private db",
                    "runner": "Python 3",
                    "toolbar": true
                },
                "OmahaServer test public": {
                    "command": "omaha-server/omaha_server/manage.py test -v 2",
                    "cwd": "/omaha-server/omaha_server",
                    "debug": false,
                    "env": {
                        "OMAHA_SERVER_PRIVATE": "False"
                    },
                    "name": "OmahaServer test public",
                    "runner": "Python 3",
                    "toolbar": true
                },
                "OmahaServer test public db": {
                    "command": "omaha-server/omaha_server/manage.py test -v 2",
                    "cwd": "/omaha-server/omaha_server",
                    "debug": false,
                    "env": {
                        "DJANGO_SETTINGS_MODULE": "omaha_server.settings_test_postgres",
                        "OMAHA_SERVER_PRIVATE": "False",
                        "PATH_TO_TEST": "omaha.tests.test_public"
                    },
                    "name": "OmahaServer test public db",
                    "runner": "Python 3",
                    "toolbar": true
                }
            }
        }
    },
  ```
* Click on `AWS Cloud9`in the menu -> `Preferences` -> `AWS Settings` -> `Credentials`, disable `AWS managed temporary credentials`
  > This is required since AWS EKS does not support temporary credentials as authentication.
* Configure your own [API Keys](https://console.aws.amazon.com/iam/home#/security_credentials)
  ```shell
  aws configure
  ```
* Let aws create your kubectl configuration for you
  ```shell
  aws eks update-kubeconfig --name {ClusterName}
  ```
* Start Postgres and Redis containers in the Cloud9 environment
  ```shell
  docker-compose up -d db redis
  ```
  > After first creation these two containers will autostart with your Cloud9 environment. To destroy them execute `docker-compose down db redis -v`.
* Start the initial db schema creation/migration from the menu `Run` -> `Run configurations` -> `OmahaServer migrate`
* Create the admin user from the menu `Run` -> `Run configurations` -> `OmahaServer create admin`
* Finally start the development server from the menu `Run` -> `Run configurations` -> `OmahaServer run server`

## Deployment to Kubernetes (AWS EKS)

### Requirements

* [AWS EKS Cluster](https://ca-central-1.console.aws.amazon.com/eks/home)
* [aws-alb-ingress-controller](https://kubernetes-sigs.github.io/aws-alb-ingress-controller/guide/controller/setup/#kubectl) running in the cluster
* [external-dns](https://kubernetes-sigs.github.io/aws-alb-ingress-controller/guide/external-dns/setup/) running in the cluster
* [Amazon EBS CSI Driver](https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html)
* [Route53](https://console.aws.amazon.com/route53/home) Hosted Zone manageable by external-dns
* [AWC Certificate Manager](https://ca-central-1.console.aws.amazon.com/acm) SSL Certificate, modify `alb.ingress.kubernetes.io/certificate-arn` or delete in `deploy/omaha_server.yaml`
* [AWS ECR](https://ca-central-1.console.aws.amazon.com/ecr/repositories) registry to store your django container, prefereable in the same region as the EKS Cluster. Modify all `image:` in `deploy/omaha_server.yaml` to match your container registry.
* [AWS S3 Bucket](https://s3.console.aws.amazon.com/s3/home) where Django static content and media files will be hosted
* [Enable IAM Roles for Kubernetes Service Accounts](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html)
* [Create IAM Policy to access S3 Bucket](https://docs.aws.amazon.com/eks/latest/userguide/create-service-account-iam-policy-and-role.html#create-service-account-iam-policy) and use the following policy:
    ```
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject"
                ],
                "Resource": [
                    "arn:aws:s3:::${YOUR_BUCKET_NAME}/*"
                ],
                "Effect": "Allow"
            }
        ]
    }
    ```
* [Create an IAM Role](https://docs.aws.amazon.com/eks/latest/userguide/create-service-account-iam-policy-and-role.html#create-service-account-iam-role) linked to policy above. The `SERVICE_ACCOUNT_NAMESPACE` should be the Kubernetes namespace you plan to deploy the server later on. The `SERVICE_ACCOUNT_NAME` is `metadata.name` of the first resource definition in `deploy/omaha-server.yaml`:
  ```
  apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: omaha-server
      annotations:
        eks.amazonaws.com/role-arn: ${IAM_ROLE_ARN}
  ```
  You need to adjust the annotation of the IAM role after creation of your role.
* Upload [CUP_PEM_KEYS](#enable-client-update-protocol-v2)

Already installed in/during Cloud9 IDE setup:
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
* [kubectl](#cloud9-environment-configuration)

### Deployment

    # kubectl config
    $(aws eks --region {REGION} update-kubeconfig --name {CLUSTER_NAME} --no-include-email)

    # deploy redis and postgres first (only needs to be done once)
    kubectl [-n {NAMESPACE}] apply -f deploy/redis.yaml deploy/postgres.yaml

    # /!\ modify the configuration to your needs first: deploy/omaha-server.yaml /!\
    kubectl [-n {NAMESPACE}] apply -f deploy/omaha-server.yaml

## Omaha Server commands/tools

### Statistics

All statistics are stored in Redis. In order not to lose all data, we recommend to set up the backing up process.

Required `userid`. [Including user id into request](https://github.com/Crystalnix/omaha/wiki/Omaha-Client-working-with-protocol#including-user-id-into-request)

### Utils

A command for generating fake data such as requests, events and statistics:

```shell
# Usage: ./manage.py generate_fake_data [options] <app_id>
# Options:
#     --count=COUNT         Total number of data values (default: 100)
python manage.py generate_fake_data {F07B3878-CD6F-4B96-B52F-95C4D2} --count=20
```

A command for generating fake statistics:

```shell
# Usage: ./manage.py generate_fake_statistics [options]
# Options:
#     --count=COUNT         Total number of data values (default: 100)
python manage.py generate_fake_statistics --count=3000
```

A command for generating fake live data:

```shell
# Usage: ./manage.py generate_fake_live_data <app_id>
#
python manage.py generate_fake_live_data {c00b6344-038f-4e51-bcb1-33ffdd812d81}
```

A command for generating fake live data for Mac:

```shell
# Usage: ./manage.py generate_fake_mac_live_data <app_name> <channel>
#
python manage.py generate_fake_mac_live_data Application alpha
```

### Enable Client Update Protocol v2

1. Use [Omaha eckeytool](https://github.com/google/omaha/tree/master/omaha/tools/eckeytool) to generate private.pem key and cup_ecdsa_pubkey.{KEYID}.h files.
2. Add cup_ecdsa_pubkey.{KEYID}.h to Omaha source directory /path/to/omaha/omaha/net/, set CupEcdsaRequestImpl::kCupProductionPublicKey in /path/to/omaha/omaha/net/cup_ecdsa_request.cc to new key and build Omaha client.
3. Add private.pem keyid and path to omaha CUP_PEM_KEYS dictionary in the [settings.py](https://github.com/DentalWings/omaha-server/blob/master/omaha_server/omaha_server/settings.py).
  On Kubernetes you will need to create it manually using `kubectl -n ${NAMESPACE} create secret generic cup-pem-keys-secret --from-file={KEY_ID}.pem=private.pem`

## Contributors

Thanks to [Abiral Shrestha](https://twitter.com/proabiral) for the security reports and suggestions.

## Copyright and license

This software is licensed under the Apache 2 license, quoted below.

Copyright 2014 [Crystalnix Limited](http://crystalnix.com)

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
