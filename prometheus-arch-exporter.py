#!/usr/bin/python

import argparse
import logging

from time import sleep
from subprocess import check_output

from prometheus_client import start_http_server, Metric, REGISTRY


PORT = 9097


class ArchCollector(object):

    def collect(self):
        packages = len(check_output('checkupdates').split(b'->'))

        metric = Metric('arch_checkupdates', 'Arch Linux Packages out of date', 'gauge')
        metric.add_sample('arch_checkupdates', value=(packages), labels={})
        yield metric

        arch_audit_text = check_output(['arch-audit', '-u'])
        security_issues = len([line for line in arch_audit_text.splitlines()[:-1] if 'from testing repos' not in line])

        metric = Metric('arch_audit', 'Arch Audit Packages', 'gauge')
        metric.add_sample('arch_audit', value=(security_issues), labels={})
        yield metric


def main():
    parser = argparse.ArgumentParser(description='Arch Linux exporter for Prometheus')
    parser.add_argument('-p', '--port', help=f'exporter exposed port (default {PORT})', type=int, default=PORT)
    args = parser.parse_args()

    start_http_server(args.port)
    REGISTRY.register(ArchCollector())

    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
