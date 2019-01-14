#!/usr/bin/python

import time
from subprocess import check_output

from prometheus_client import start_http_server, Metric, REGISTRY


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


if __name__ == "__main__":
    start_http_server(9097)
    REGISTRY.register(ArchCollector())
    while True:
        time.sleep(10)
