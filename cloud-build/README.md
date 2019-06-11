This folder contains Cloud Build artifacts:
- `cloudbuild.yaml` - a Cloud Build config file
- `build.sh` - a bash script template that uses `gcloud builds submit` to configure and start the build
- `kfp-compiler-builder/Dockerfile` - Dockerfile for an image used by the builds custom steps.
- `helpers/update_image_name_in_specs.py` is a utility script to update the `image` node in the component specs. 
- `helpers/update_

