import os
import sys
import signal
import logging
import time

import click
from kubernetes.config import new_client_from_config, load_incluster_config
from kubernetes.config.config_exception import ConfigException
from kubernetes import client

logger = logging.getLogger('pod_lister')

RUNNING = True


def stop_app(s, f):
    global RUNNING
    RUNNING = False
    logger.info("Stopping app...")


@click.command()
@click.option('--config', default='', help="Kubernetes Config file")
@click.option('--context', default=None, help="Kubernetes Context to use")
@click.option('--debug', is_flag=True, help="Debug mode")
def main(config, context, debug):
    logging.basicConfig(level=debug and logging.DEBUG or logging.INFO)

    try:
        api_client = load_incluster_config()
        logger.info("Using in cluster config.")
    except ConfigException:
        config = config or os.path.abspath(os.path.expanduser('~/.kube/config'))
        logger.info("Using config file: {}".format(config))

        api_client = new_client_from_config(config_file=config)

    signal.signal(signal.SIGTERM, stop_app)

    logger.info("Starting app...")
    core_api = client.CoreV1Api(api_client=api_client)
    while RUNNING:
        result = core_api.list_pod_for_all_namespaces(watch=False)
        for i in result.items:
            print("%s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

        time.sleep(3)


if __name__ == '__main__':
    main()
