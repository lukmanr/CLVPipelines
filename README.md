# CLVPipelines

## Install GKE

```
#!/bin/bash
  
CLUSTERNAME=mykfp
ZONE=us-central1-b
gcloud config set compute/zone $ZONE
gcloud beta container clusters create $CLUSTERNAME \
  --cluster-version 1.11.8-gke.6 --enable-autoupgrade \
  --zone $ZONE \
  --scopes cloud-platform \
  --enable-cloud-logging \
  --enable-cloud-monitoring \
  --machine-type n1-standard-2 \
  --num-nodes 4
kubectl create clusterrolebinding ml-pipeline-admin-binding --clusterrole=cluster-admin --user=$(gcloud config get-value account)
```

## Install Kubeflow pipelines
```
#!/bin/bash
PIPELINE_VERSION=0.1.7
kubectl create -f https://storage.googleapis.com/ml-pipeline/release/$PIPELINE_VERSION/bootstrapper.yaml
```
## Monitor installation
```
#!/bin/bash
jobname=$(kubectl get job | tail -1 | awk '{print $1}')
kubectl wait --for=condition=complete --timeout=5m $jobname
```
