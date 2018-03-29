#!/bin/bash

env="dev"

path_to_config=/home/admssa/.kube

tag="018227650373.dkr.ecr.us-west-2.amazonaws.com/kubbuilder:latest"
$(aws ecr get-login --no-include-email --region us-west-2)
docker build -t ${tag} -f Dockerfile .
docker push ${tag}
kubectl -n nlu create configmap kuber-conf-map --from-file=${path_to_config}
kubectl -n nlu create -f ./kuber_deploy/${env}/kubbuilder.yaml


