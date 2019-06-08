import fire
import kfp


def run(host, client_id, experiment, run_name, pipeline_file, arguments):
  "Submits a KFP pipeline for execution"

  client = kfp.Client(host, client_id)

  experiment_ref = client.create_experiment(experiment)

  run = client.run_pipeline(experiment_ref.id, run_name, pipeline_file,
                            arguments)
  print("Run submitted:")
  print("    Run ID: {}".format(run.id))
  print("    Experiment: {}".format(experiment))
  print("    Pipeline: {}".format(pipeline_file))
  print("    Arguments:")
  for name, value in arguments.items():
    print("      {}:  {}".format(name, value))
  print("Waiting for completion ...")

  # Wait for completion
  result = client.wait_for_run_completion(run.id, timeout=6000)


if __name__ == "__main__":
  fire.Fire(run)