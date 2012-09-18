# Copyright 2012 OpenStack LLC.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import argparse
import logging

from quantumclient.common import utils
from quantumclient.quantum import v2_0 as quantumv20
from quantumclient.quantum.v2_0 import CreateCommand
from quantumclient.quantum.v2_0 import DeleteCommand
from quantumclient.quantum.v2_0 import ListCommand
from quantumclient.quantum.v2_0 import ShowCommand
from quantumclient.quantum.v2_0 import UpdateCommand


def _format_fixed_ips(port):
    try:
        return '\n'.join([utils.dumps(ip) for ip in port['fixed_ips']])
    except Exception:
        return ''


class ListPort(ListCommand):
    """List networks that belong to a given tenant."""

    resource = 'port'
    log = logging.getLogger(__name__ + '.ListPort')
    _formatters = {'fixed_ips': _format_fixed_ips, }
    list_columns = ['id', 'name', 'mac_address', 'fixed_ips']


class ShowPort(ShowCommand):
    """Show information of a given port."""

    resource = 'port'
    log = logging.getLogger(__name__ + '.ShowPort')


class CreatePort(CreateCommand):
    """Create a port for a given tenant."""

    resource = 'port'
    log = logging.getLogger(__name__ + '.CreatePort')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--name',
            help='name of this port')
        parser.add_argument(
            '--admin-state-down',
            default=True, action='store_false',
            help='set admin state up to false')
        parser.add_argument(
            '--admin_state_down',
            action='store_false',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--mac-address',
            help='mac address of this port')
        parser.add_argument(
            '--mac_address',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--device-id',
            help='device id of this port')
        parser.add_argument(
            '--device_id',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--fixed-ip',
            action='append',
            help='desired IP for this port: '
            'subnet_id=<name_or_id>,ip_address=<ip>, '
            'can be repeated')
        parser.add_argument(
            '--fixed_ip',
            action='append',
            help=argparse.SUPPRESS)
        parser.add_argument(
            'network_id', metavar='network',
            help='Network id or name this port belongs to')

    def args2body(self, parsed_args):
        _network_id = quantumv20.find_resourceid_by_name_or_id(
            self.get_client(), 'network', parsed_args.network_id)
        body = {'port': {'admin_state_up': parsed_args.admin_state_down,
                         'network_id': _network_id, }, }
        if parsed_args.mac_address:
            body['port'].update({'mac_address': parsed_args.mac_address})
        if parsed_args.device_id:
            body['port'].update({'device_id': parsed_args.device_id})
        if parsed_args.tenant_id:
            body['port'].update({'tenant_id': parsed_args.tenant_id})
        if parsed_args.name:
            body['port'].update({'name': parsed_args.name})
        ips = []
        if parsed_args.fixed_ip:
            for ip_spec in parsed_args.fixed_ip:
                ip_dict = utils.str2dict(ip_spec)
                if 'subnet_id' in ip_dict:
                    subnet_name_id = ip_dict['subnet_id']
                    _subnet_id = quantumv20.find_resourceid_by_name_or_id(
                        self.get_client(), 'subnet', subnet_name_id)
                    ip_dict['subnet_id'] = _subnet_id
                ips.append(ip_dict)
        if ips:
            body['port'].update({'fixed_ips': ips})
        return body


class DeletePort(DeleteCommand):
    """Delete a given port."""

    resource = 'port'
    log = logging.getLogger(__name__ + '.DeletePort')


class UpdatePort(UpdateCommand):
    """Update port's information."""

    resource = 'port'
    log = logging.getLogger(__name__ + '.UpdatePort')
