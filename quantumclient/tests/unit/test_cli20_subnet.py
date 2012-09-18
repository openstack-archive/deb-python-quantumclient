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
from quantumclient.quantum.v2_0.subnet import CreateSubnet
from quantumclient.quantum.v2_0.subnet import ListSubnet
from quantumclient.quantum.v2_0.subnet import UpdateSubnet
from quantumclient.quantum.v2_0.subnet import ShowSubnet
from quantumclient.quantum.v2_0.subnet import DeleteSubnet


class CLITestV20Subnet(CLITestV20Base):

    def test_create_subnet(self):
        """Create subnet: --gateway gateway netid cidr."""
        resource = 'subnet'
        cmd = CreateSubnet(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'cidrvalue'
        gateway = 'gatewayvalue'
        args = ['--gateway', gateway, netid, cidr]
        position_names = ['ip_version', 'network_id', 'cidr', 'gateway_ip']
        position_values = [4, netid, cidr, gateway]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values)

    def test_create_subnet_with_no_gateway(self):
        """Create subnet: --no-gateway netid cidr"""
        resource = 'subnet'
        cmd = CreateSubnet(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'cidrvalue'
        args = ['--no-gateway',  netid, cidr]
        position_names = ['ip_version', 'network_id', 'cidr', 'gateway_ip']
        position_values = [4, netid, cidr, None]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values)

    def test_create_subnet_with_bad_gateway_option(self):
        """Create sbunet: --no-gateway netid cidr"""
        resource = 'subnet'
        cmd = CreateSubnet(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'cidrvalue'
        gateway = 'gatewayvalue'
        args = ['--gateway',  gateway, '--no-gateway',  netid, cidr]
        position_names = ['ip_version', 'network_id', 'cidr', 'gateway_ip']
        position_values = [4, netid, cidr, None]
        try:
            _str = self._test_create_resource(resource, cmd, name, myid, args,
                                              position_names, position_values)
        except:
            return
        self.fail('No exception for bad gateway option')

    def test_create_subnet_tenant(self):
        """Create subnet: --tenant_id tenantid netid cidr."""
        resource = 'subnet'
        cmd = CreateSubnet(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid', netid, cidr]
        position_names = ['ip_version', 'network_id', 'cidr']
        position_values = [4, netid, cidr]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tenant_id='tenantid')

    def test_create_subnet_tags(self):
        """Create subnet: netid cidr --tags a b."""
        resource = 'subnet'
        cmd = CreateSubnet(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = [netid, cidr, '--tags', 'a', 'b']
        position_names = ['ip_version', 'network_id', 'cidr']
        position_values = [4, netid, cidr]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tags=['a', 'b'])

    def test_create_subnet_allocation_pool(self):
        """Create subnet: --tenant_id tenantid <allocation_pool> netid cidr.
        The <allocation_pool> is --allocation_pool start=1.1.1.10,end=1.1.1.20
        """
        resource = 'subnet'
        cmd = CreateSubnet(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--allocation_pool', 'start=1.1.1.10,end=1.1.1.20',
                netid, cidr]
        position_names = ['ip_version', 'allocation_pools', 'network_id',
                          'cidr']
        pool = [{'start': '1.1.1.10', 'end': '1.1.1.20'}]
        position_values = [4, pool, netid, cidr]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tenant_id='tenantid')

    def test_create_subnet_allocation_pools(self):
        """Create subnet: --tenant-id tenantid <pools> netid cidr.
        The <pools> are --allocation_pool start=1.1.1.10,end=1.1.1.20 and
        --allocation_pool start=1.1.1.30,end=1.1.1.40
        """
        resource = 'subnet'
        cmd = CreateSubnet(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        netid = 'netid'
        cidr = 'prefixvalue'
        args = ['--tenant_id', 'tenantid',
                '--allocation_pool', 'start=1.1.1.10,end=1.1.1.20',
                '--allocation_pool', 'start=1.1.1.30,end=1.1.1.40',
                netid, cidr]
        position_names = ['ip_version', 'allocation_pools', 'network_id',
                          'cidr']
        pools = [{'start': '1.1.1.10', 'end': '1.1.1.20'},
                 {'start': '1.1.1.30', 'end': '1.1.1.40'}]
        position_values = [4, pools, netid, cidr]
        _str = self._test_create_resource(resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tenant_id='tenantid')

    def test_list_subnets_detail(self):
        """List subnets: -D."""
        resources = "subnets"
        cmd = ListSubnet(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_subnets_tags(self):
        """List subnets: -- --tags a b."""
        resources = "subnets"
        cmd = ListSubnet(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, tags=['a', 'b'])

    def test_list_subnets_detail_tags(self):
        """List subnets: -D -- --tags a b."""
        resources = "subnets"
        cmd = ListSubnet(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, detail=True, tags=['a', 'b'])

    def test_list_subnets_fields(self):
        """List subnets: --fields a --fields b -- --fields c d."""
        resources = "subnets"
        cmd = ListSubnet(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  fields_1=['a', 'b'], fields_2=['c', 'd'])

    def test_update_subnet(self):
        """Update subnet: myid --name myname --tags a b."""
        resource = 'subnet'
        cmd = UpdateSubnet(MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'myname',
                                    '--tags', 'a', 'b'],
                                   {'name': 'myname', 'tags': ['a', 'b'], }
                                   )

    def test_show_subnet(self):
        """Show subnet: --fields id --fields name myid."""
        resource = 'subnet'
        cmd = ShowSubnet(MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id', 'name'])

    def test_delete_subnet(self):
        """Delete subnet: subnetid."""
        resource = 'subnet'
        cmd = DeleteSubnet(MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)
