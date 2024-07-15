# omaha-server

[![Build Status](https://travis-ci.com/dentalwings/omaha-server.svg?branch=master)](https://travis-ci.com/dentalwings/omaha-server)
[![Coverage Status](https://coveralls.io/repos/github/dentalwings/omaha-server/badge.svg?branch=travis-tests)](https://coveralls.io/github/dentalwings/omaha-server?branch=travis-tests)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/dentalwings/omaha-server/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/dentalwings/omaha-server/?branch=master)
[![Apache License, Version 2.0](https://img.shields.io/badge/license-Apache%202.0-red.svg)](https://github.com/dentalwings/omaha-server/blob/master/LICENSE)

**Omaha server no longer supports Python version 2 and Django 1.11 or lower version. If you need the old version of the application, then check the old_master branch.**

Google Omaha server implementation and Sparkle (mac) feed management.

Currently, Crystalnix's implementation is integrated into the updating processes of several organizations for products that require sophisticated update logic and advanced usage statistics. Crystalnix provide additional support and further enhancement on a contract basis. For a case study and enquiries please refer to [Crystalnix website](https://www.crystalnix.com/case-study/google-omaha)

## Setting up a local development environment

### Requirements

* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* a code editor such as [VSCode](https://code.visualstudio.com/download)
* AWS API key

### Set up

Create a `.env` file at the root of the project and add your AWS key
```bash
AWS_ACCESS_KEY_ID=<replace-me>
AWS_SECRET_ACCESS_KEY=<replace-me>
```
Generate your local pem key and place it in the volume folder
```bash
mkdir cup_pem_key
openssl ecparam -out cup_pem_key/1.pem -name prime256v1 -genkey
```

Start the service using docker compose
```bash
docker compose up -d
```
> :warning: **The above command might have to be started a second time due to the postgress container not beeing fully started when django_migration starts**


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
