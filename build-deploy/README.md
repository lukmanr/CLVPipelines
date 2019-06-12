This folder contains Cloud Build artifacts:
- `cloudbuild.yaml` - a Cloud Build config file
- `build.sh` - a bash script template that uses `gcloud builds submit` to configure and start the build
- `kfp-compiler-builder/Dockerfile` - Dockerfile for an image used by the builds custom steps.
- `helpers` - a folder with utility scripts used during the build
  - `update_image_name_in_specs.py` - updating the `image` node in the component specs. 
  - `helpers/update_settings_file.py` - updating the pipelines setting file





