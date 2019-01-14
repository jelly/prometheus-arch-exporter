#!/usr/bin/python

import argparse

from os import symlink
from shutil import rmtree
from tempfile import mkdtemp
from subprocess import check_output
from wsgiref.simple_server import make_server

from prometheus_client import make_wsgi_app, Metric, REGISTRY

from pyalpm import sync_newversion
from pycman.config import init_with_config_and_options


PORT = 9097


class PacmanConf:
    dbpath = None
    config = '/etc/pacman.conf'
    root = None
    gpgdir = None
    arch = None
    logfile = None
    cachedir = None
    debug = None


def checkupdates():
    count = 0
    options = PacmanConf()
    tempdir = mkdtemp(dir='/tmp')
    options.dbpath = tempdir
    symlink('/var/lib/pacman/local', f'{tempdir}/local')

    # Workaround for passing a different DBPath but with the system pacman.conf
    handle = init_with_config_and_options(options)
    for db in handle.get_syncdbs():
        db.update(False)

    db = handle.get_localdb()
    for pkg in db.pkgcache:
        if sync_newversion(pkg, handle.get_syncdbs()) is None:
            continue
        count += 1

    rmtree(tempdir)

    return count


class ArchCollector(object):

    def collect(self):
        packages = checkupdates()
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

    REGISTRY.register(ArchCollector())

    app = make_wsgi_app()
    httpd = make_server('', args.port, app)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
