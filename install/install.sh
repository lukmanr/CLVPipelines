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

if [[ $# < 5 ]]; then
    echo "Error: Arguments missing. [install PROJECT_ID CLUSTERNAME ZONE KFP_SA KFP_VERSION]"
    exit 1
fi

if [[ ${2} =~ ^[a-z]+[-a-z0-9]{0,38}[a-z0-9]+$ ]]; then
  echo "Cluster name: valid (matches '^[a-z]+[-a-z0-9]{0,38}[a-z0-9]+$')"
else
  echo "Cluster name invalid (does not match '^[a-z]+[-a-z0-9]{0,38}[a-z0-9]+$')"
  exit 1
fi

# 1. Set variables. If you are stepping through the script manually set these directly from Bash prompt
PROJECT_ID=${1}
PROJECT_NUMBER=$(gcloud projects list --filter="$PROJECT_ID" --format="value(PROJECT_NUMBER)")
CLUSTERNAME=${2}
ZONE=${3}
SA_NAME=${4}
KFP_VERSION=${5}

# 2. Set the default project ID
echo "Setting a default project to: "${1}
gcloud config set project $PROJECT_ID

# 3. Create GKE cluster
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

# 4. Install KFP
echo "Installing KFP version: "${KFP_VERSION}
NAMESPACE_EXISTS=$(kubectl get namespace kubeflow -o=name)
if [ -n "$NAMESPACE_EXISTS" ]
then
  echo "Namespace: kubeflow already exists. Deleting the existing namespace and re-installing KFP."
  kubectl delete namespace kubeflow
fi
kubectl apply -f https://raw.githubusercontent.com/kubeflow/pipelines/$KFP_VERSION/manifests/namespaced-install.yaml

echo "Sleeping for 5 minutes to let services start"
sleep 5m

# 5. Create a service account to be used by pipelines. If the account with that name exists, re-use it
echo "Creating service account: "${SA_NAME}
SA_EXISTS=$(gcloud beta iam service-accounts list | grep ${SA_NAME})
if [ -z "$SA_EXISTS" ]
then
  gcloud beta iam service-accounts create ${SA_NAME}  \
  --description "Kubeflow Pipelines Service Account" \
  --display-name "Kubeflow Pipelines SA"
else
  echo "Service account: "${SA_NAME}" already exists. Re-using ..."
fi

# 6. Create a service account private key in the current folder
echo "Creating service account key: key.json"
gcloud iam service-accounts keys create key.json \
--iam-account ${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

# 7. Save the key as a Kubernetes secret
echo "Saving the key as a secret: user-gcp-sa"
kubectl create secret -n kubeflow generic user-gcp-sa --from-file=user-gcp-sa.json=key.json

# 8. Delete the key
rm key.json

# 9. Assign the service account to Cloud Storage admin role
echo "Assigning Cloud Storage permissions to: "$SA_NAME
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
--member serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com \
--role roles/storage.admin \
--no-user-output-enabled

# 10. Assign the service account to Big Query admin role
echo "Assigning BigQuery permissions to: "$SA_NAME
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
--member serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com \
--role roles/bigquery.admin \
--no-user-output-enabled

# 11. Assigne the service account to AutoML admin role
echo "Assigning AutoML permissions to: "$SA_NAME
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
--member serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com \
--role roles/automl.admin \
--no-user-output-enabled

# 12. Assigne the service account to AutoML Predictor role
echo "Assigning AutoML Predict permissions to: "$SA_NAME
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
--member serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com \
--role roles/automl.predictor \
--no-user-output-enabled

# 13. Print out the KFP UI endpoint
KFP_UI_URL="https://"$(kubectl describe configmap inverse-proxy-config -n kubeflow | grep "googleusercontent.com")
echo "Kubeflow Pipelines installation complete"
echo "You can access KFP UI at: "${KFP_UI_URL}
