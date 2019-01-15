# prometheus-arch-exporter

This Prometheus exporter collects Arch Linux specific metrics such as out of date packages and the amount of vulnerable packages.

## Dependencies

* python3
* python-prometheus_client
* pyalpm
* requests

## Usage

Run the exporter
```bash
python prometheus-arch-exporter.py
```

The default port is 9097, visit metrics in [localhost:9097/](http://localhost:9097/)

## Systemd

A systemd service is available with hardening options enabled.
