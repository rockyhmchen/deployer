#!/usr/bin/env python

import argparse
import yaml
import os.path
import logging
import subprocess

logging.basicConfig(level=logging.INFO)

class Manifest:
    def __init__(self, deployment, config_map, secret):
        self.plan = None
        self.deployment = deployment
        self.config_map = config_map
        self.secret = secret

def verify_plan(plan_file):
    """

    :param plan_file:
    :return:
    """
    logging.info("verify_plan")
    return True

def get_plan(plan_file):
    """

    :param plan_file:
    :return:
    """

    is_plan_valid = verify_plan(plan_file)
    if not is_plan_valid:
        raise Exception("Invalid plan file")

    logging.info("get_plan")
    with open(plan_file, "r") as f:
        plan = yaml.full_load(f)

    full_path = os.path.abspath(plan_file)
    dir_name = os.path.dirname(full_path)

    main_plan = plan["plan"]
    manifest = main_plan["manifest"]

    deployment_yaml_full_path = get_full_path(manifest, "deployment", dir_name)
    config_map_yaml_full_path = get_full_path(manifest, "config_map", dir_name)
    secret_yaml_full_path = get_full_path(manifest, "secret", dir_name)

    logging.info(f"deployment yaml: {deployment_yaml_full_path}")
    logging.info(f"config_map yaml: {config_map_yaml_full_path}")
    logging.info(f"secret yaml: {secret_yaml_full_path}")

    return Manifest(deployment_yaml_full_path, config_map_yaml_full_path, secret_yaml_full_path)

def get_full_path(manifest, key, dir_name):
    """

    :param manifest:
    :return:
    """
    yaml_file = manifest[key]
    yaml_full_path = os.path.join(dir_name, yaml_file)
    if not os.path.exists(yaml_full_path):
        error_message = f"{yaml_file} is missing"
        raise Exception(error_message)

    return yaml_full_path

def apply_config_map(config_map_yaml, namespace):
    """

    :param config_map_yaml:
    :return:
    """
    logging.info("apply_config_map")
    subprocess.run(["kubectl", "--namespace", namespace, "apply", "-f", config_map_yaml])

def apply_secret(secret_yaml, namespace):
    """

    :param secret_yaml:
    :return:
    """
    logging.info("apply_secret")
    subprocess.run(["kubectl", "--namespace", namespace, "apply", "-f", secret_yaml])

def apply_deployment(deployment_yaml, docker_image, namespace):
    """

    :param deployment_yaml:
    :return:
    """
    logging.info("apply_deployment")
    subprocess.run(["kubectl", "--namespace", namespace, "apply", "-f", deployment_yaml])

def main():
    """

    :return:
    """
    parser = argparse.ArgumentParser(description="test description")
    parser.add_argument("--plan", help="The path of the deploy plan")
    parser.add_argument("--image", help="Full docker image path including tag")
    parser.add_argument("--namespace", help="Target namespace")
    args = parser.parse_args()

    plan_file = args.plan
    docker_image = args.image
    namespace = args.namespace


    plan = get_plan(plan_file)

    apply_secret(plan.secret, namespace)
    apply_config_map(plan.config_map, namespace)
    apply_deployment(plan.deployment, docker_image, namespace)


if __name__ == "__main__":
    main()