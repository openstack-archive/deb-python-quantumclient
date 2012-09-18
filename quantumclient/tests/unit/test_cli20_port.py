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

import sys

from quantumclient.tests.unit.test_cli20 import CLITestV20Base
from quantumclient.tests.unit.test_cli20 import MyApp
from quantumclient.quantum.v2_0.port import CreatePort
from quantumclient.quantum.v2_0.port import ListPort
from quantumclient.quantum.v2_0.port import UpdatePort
from quantumclient.quantum.v2_0.port import ShowPort
from quantumclient.quantum.v2_0.port import DeletePort


class CLITestV20Port(CLITestV20Base):

    def test_create_port(self):
        """Create port: netid."""
        resource = 'port'
        cmd = CreatePort(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        args = [netid]
        position_names = ['network_id']
        position_values = []
        position_values.extend([netid])
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values)

    def test_create_port_full(self):
        """Create port: --mac_address mac --device_id deviceid netid."""
        resource = 'port'
        cmd = CreatePort(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        args = ['--mac_address', 'mac', '--device_id', 'deviceid', netid]
        position_names = ['network_id', 'mac_address', 'device_id']
        position_values = [netid, 'mac', 'deviceid']
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values)

        # Test dashed options
        args = ['--mac-address', 'mac', '--device-id', 'deviceid', netid]
        position_names = ['network_id', 'mac_address', 'device_id']
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values)

    def test_create_port_tenant(self):
        """Create port: --tenant_id tenantid netid."""
        resource = 'port'
        cmd = CreatePort(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        args = ['--tenant_id', 'tenantid', netid, ]
        position_names = ['network_id']
        position_values = []
        position_values.extend([netid])
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tenant_id='tenantid')

        # Test dashed options
        args = ['--tenant-id', 'tenantid', netid, ]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tenant_id='tenantid')

    def test_create_port_tags(self):
        """Create port: netid mac_address device_id --tags a b."""
        resource = 'port'
        cmd = CreatePort(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        args = [netid, '--tags', 'a', 'b']
        position_names = ['network_id']
        position_values = []
        position_values.extend([netid])
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tags=['a', 'b'])

    def test_list_ports(self):
        """List ports: -D."""
        resources = "ports"
        cmd = ListPort(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_ports_tags(self):
        """List ports: -- --tags a b."""
        resources = "ports"
        cmd = ListPort(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, tags=['a', 'b'])

    def test_list_ports_detail_tags(self):
        """List ports: -D -- --tags a b."""
        resources = "ports"
        cmd = ListPort(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, detail=True, tags=['a', 'b'])

    def test_list_ports_fields(self):
        """List ports: --fields a --fields b -- --fields c d."""
        resources = "ports"
        cmd = ListPort(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  fields_1=['a', 'b'], fields_2=['c', 'd'])

    def test_update_port(self):
        """Update port: myid --name myname --tags a b."""
        resource = 'port'
        cmd = UpdatePort(MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'myname',
                                    '--tags', 'a', 'b'],
                                   {'name': 'myname', 'tags': ['a', 'b'], }
                                   )

    def test_show_port(self):
        """Show port: --fields id --fields name myid."""
        resource = 'port'
        cmd = ShowPort(MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id', 'name'])

    def test_delete_port(self):
        """Delete port: myid."""
        resource = 'port'
        cmd = DeletePort(MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)
