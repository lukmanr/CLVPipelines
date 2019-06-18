#!/bin/bash
# Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This is the Kubeflow Pipelines installation script

if [[ $# < 6 ]]; then
    echo "Error: Arguments missing. [install PROJECT_ID CLUSTERNAME ZONE KFP_SA KEY_PATH KFP_VERSION]"
    exit 1
fi

PROJECT_ID=${1}
PROJECT_NUMBER=$(gcloud projects list --filter="$PROJECT_ID" --format="value(PROJECT_NUMBER)")
CLUSTERNAME=${2}
ZONE=${3}
SA_NAME=${4}
KEY_PATH=${5}
KFP_VERSION=${6}

echo "Setting a default project to: "${1}
gcloud config set project $PROJECT_ID

echo "Creating service account: "${SA_NAME}
SA_EXISTS=$(gcloud beta iam service-accounts list | grep ${SA_NAME})
if [ -n "$SA_EXISTS" ]
then
  echo "Service account: "${SA_NAME}" already exists. Deleting an re-creating the account." 
  gcloud beta iam service-accounts delete ${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com -q 
fi
gcloud beta iam service-accounts create ${SA_NAME}  \
--description "Kubeflow Pipelines Service Account" \
--display-name "Kubeflow Pipelines SA"

echo "Creating service account key: "${KEY_PATH}
gcloud iam service-accounts keys create ${KEY_PATH} \
--iam-account ${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

echo "Saving the key as a secret: user-gcp-sa"
SECRET_EXISTS=$(kubectl get secrets | grep -q "user-gcp-sa")
if [ -n "$SECRET_EXISTS" ]
then
  echo "user-gcp-sa secret already exists. Deleting and re-creating ..."
  kubectl delete secret user-gcp-sa -n kubeflow
fi
kubectl create secret -n kubeflow generic user-gcp-sa --from-file=user-gcp-sa.json=${KEY_PATH}

echo "Assigning Cloud Storage permissions to: "$SA_NAME
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
--member serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com \
--role roles/storage.admin \
--no-user-output-enabled

echo "Assigning BigQuery permissions to: "$SA_NAME
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
--member serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com \
--role roles/bigquery.admin \
--no-user-output-enabled

echo "Assigning AutoML permissions to: "$SA_NAME
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
--member serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com \
--role roles/automl.admin \
--no-user-output-enabled

echo "Creating GKE:"${2}" in zone: "${3} ...
CLUSTER_EXISTS=$(gcloud container clusters list|grep ${CLUSTERNAME})
if [ -z "$CLUSTER_EXISTS" ]
then 
  gcloud beta container clusters create $CLUSTERNAME \
  --zone $ZONE \
  --scopes cloud-platform
else
  echo "Cluster: "${CLUSTERNAME}" already exists. Skipping installation"
fi

echo "Installing KFP version: "${KFP_VERSION}
NAMESPACE_EXISTS=$(kubectl get namespace kubeflow -o=name)
if [ -n "$NAMESPACE_EXISTS" ]
then
  echo "Namespace: kubeflow already exists. Deleting the existing namespace and re-installing KFP."
  kubectl delete namespace kubeflow 
fi
kubectl apply -f https://raw.githubusercontent.com/kubeflow/pipelines/$KFP_VERSION/manifests/namespaced-install.yaml


echo "Sleeping for 5 minutes before retrieving Inverting Proxy endpoint"
sleep 5m 

KFP_UI_URL="https://"$(kubectl describe configmap inverse-proxy-config -n kubeflow | grep "googleusercontent.com")
echo "Kubeflow Pipelines installation complete"
echo "You can access KFP UI at: "${KFP_UI_URL}
