"""
Napalm driver for Bird.

Read napalm.readthedocs.org for more information.
"""

from napalm_base.base import NetworkDriver
from napalm_base.exceptions import ConnectionException, SessionLockedException, \
                                   MergeConfigException, ReplaceConfigException,\
                                   CommandErrorException
# netaddr installed by napalm
from netaddr import IPAddress


import pybird


class BirdDriver(NetworkDriver):
    """Napalm driver for Bird."""
    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """Constructor."""
        self.device = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout

        if optional_args is None or 'socket_file' not in optional_args:
            raise ValueError("socket_file needs to be defined")

        self.socket_file = optional_args['socket_file']

        self.device = pybird.PyBird(self.socket_file, self.hostname, self.username, self.password)

    def open(self):
        """Implementation of NAPALM method open."""
        pass

    def close(self):
        """Implementation of NAPALM method close."""
        pass

    def get_bgp_neighbors(self):
        """Return BGP neighbors details."""

        router_id = self.device.get_bird_status()['router_id']

        field_map = {
            # 'local_as'
            'asn': 'remote_as',
            'router_id': 'remote_id',
            'up': 'is_up',
            'description': 'description',
            # 'uptime'
            }

        rv = {
            'router_id': router_id,
            'peers': {},
            }

        for peer in self.device.get_peer_status():
            if peer['protocol'] != 'BGP':
                continue

            addr = IPAddress(peer['address'])

            row = {v: peer.get(k, None) for k, v in field_map.items()}
            row['is_enabled'] = True
            row['address_family'] = {
                'ipv{}'.format(addr.version): {
                    'received_prefixes': 0,
                    'accepted_prefixes': peer['routes_imported'],
                    'sent_prefixes': 0,
                    }
                }
            rv['peers'][addr] = row

        return rv

