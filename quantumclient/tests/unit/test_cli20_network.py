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

import mox
from mox import (ContainsKeyValue, IgnoreArg, IsA)

from quantumclient.common import exceptions
from quantumclient.common import utils
from quantumclient.quantum.v2_0.network import CreateNetwork
from quantumclient.quantum.v2_0.network import DeleteNetwork
from quantumclient.quantum.v2_0.network import ListExternalNetwork
from quantumclient.quantum.v2_0.network import ListNetwork
from quantumclient.quantum.v2_0.network import ShowNetwork
from quantumclient.quantum.v2_0.network import UpdateNetwork
from quantumclient import shell
from quantumclient.tests.unit import test_cli20
from quantumclient.tests.unit.test_cli20 import CLITestV20Base
from quantumclient.tests.unit.test_cli20 import MyApp


class CLITestV20Network(CLITestV20Base):
    def test_create_network(self):
        """Create net: myname."""
        resource = 'network'
        cmd = CreateNetwork(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        args = [name, ]
        position_names = ['name', ]
        position_values = [name, ]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values)

    def test_create_network_tenant(self):
        """Create net: --tenant_id tenantid myname."""
        resource = 'network'
        cmd = CreateNetwork(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        args = ['--tenant_id', 'tenantid', name]
        position_names = ['name', ]
        position_values = [name, ]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

        # Test dashed options
        args = ['--tenant-id', 'tenantid', name]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tenant_id='tenantid')

    def test_create_network_tags(self):
        """Create net: myname --tags a b."""
        resource = 'network'
        cmd = CreateNetwork(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        args = [name, '--tags', 'a', 'b']
        position_names = ['name', ]
        position_values = [name, ]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   tags=['a', 'b'])

    def test_create_network_state(self):
        """Create net: --admin_state_down myname."""
        resource = 'network'
        cmd = CreateNetwork(MyApp(sys.stdout), None)
        name = 'myname'
        myid = 'myid'
        args = ['--admin_state_down', name, ]
        position_names = ['name', ]
        position_values = [name, ]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   admin_state_up=False)

        # Test dashed options
        args = ['--admin-state-down', name, ]
        self._test_create_resource(resource, cmd, name, myid, args,
                                   position_names, position_values,
                                   admin_state_up=False)

    def test_list_nets_empty_with_column(self):
        resources = "networks"
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        self.mox.StubOutWithMock(ListNetwork, "extend_list")
        ListNetwork.extend_list(IsA(list), IgnoreArg())
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        reses = {resources: []}
        resstr = self.client.serialize(reses)
        # url method body
        query = "id=myfakeid"
        args = ['-c', 'id', '--', '--id', 'myfakeid']
        path = getattr(self.client, resources + "_path")
        self.client.httpclient.request(
            test_cli20.end_url(path, query), 'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                'X-Auth-Token',
                test_cli20.TOKEN)).AndReturn(
                    (test_cli20.MyResp(200), resstr))
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("list_" + resources)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        self.assertEquals('\n', _str)

    def _test_list_networks(self, cmd, detail=False, tags=[],
                            fields_1=[], fields_2=[], page_size=None,
                            sort_key=[], sort_dir=[]):
        resources = "networks"
        self.mox.StubOutWithMock(ListNetwork, "extend_list")
        ListNetwork.extend_list(IsA(list), IgnoreArg())
        self._test_list_resources(resources, cmd, detail, tags,
                                  fields_1, fields_2, page_size=page_size,
                                  sort_key=sort_key, sort_dir=sort_dir)

    def test_list_nets_pagination(self):
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self.mox.StubOutWithMock(ListNetwork, "extend_list")
        ListNetwork.extend_list(IsA(list), IgnoreArg())
        self._test_list_resources_with_pagination("networks", cmd)

    def test_list_nets_sort(self):
        """list nets: --sort-key name --sort-key id --sort-dir asc
        --sort-dir desc
        """
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_networks(cmd, sort_key=['name', 'id'],
                                 sort_dir=['asc', 'desc'])

    def test_list_nets_sort_with_keys_more_than_dirs(self):
        """list nets: --sort-key name --sort-key id --sort-dir desc
        """
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_networks(cmd, sort_key=['name', 'id'],
                                 sort_dir=['desc'])

    def test_list_nets_sort_with_dirs_more_than_keys(self):
        """list nets: --sort-key name --sort-dir desc --sort-dir asc
        """
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_networks(cmd, sort_key=['name'],
                                 sort_dir=['desc', 'asc'])

    def test_list_nets_limit(self):
        """list nets: -P"""
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_networks(cmd, page_size=1000)

    def test_list_nets_detail(self):
        """list nets: -D."""
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_networks(cmd, True)

    def test_list_nets_tags(self):
        """List nets: -- --tags a b."""
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_networks(cmd, tags=['a', 'b'])

    def test_list_nets_detail_tags(self):
        """List nets: -D -- --tags a b."""
        resources = "networks"
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_networks(cmd, detail=True, tags=['a', 'b'])

    def _test_list_nets_extend_subnets(self, data, expected):
        def setup_list_stub(resources, data, query):
            reses = {resources: data}
            resstr = self.client.serialize(reses)
            resp = (test_cli20.MyResp(200), resstr)
            path = getattr(self.client, resources + '_path')
            self.client.httpclient.request(
                test_cli20.end_url(path, query), 'GET',
                body=None,
                headers=ContainsKeyValue(
                    'X-Auth-Token', test_cli20.TOKEN)).AndReturn(resp)

        resources = "networks"
        cmd = ListNetwork(test_cli20.MyApp(sys.stdout), None)
        self.mox.StubOutWithMock(cmd, 'get_client')
        self.mox.StubOutWithMock(self.client.httpclient, 'request')
        cmd.get_client().AndReturn(self.client)
        setup_list_stub('networks', data, '')
        cmd.get_client().AndReturn(self.client)
        filters = ''
        for n in data:
            for s in n['subnets']:
                filters = filters + "&id=%s" % s
        setup_list_stub('subnets',
                        [{'id': 'mysubid1', 'cidr': '192.168.1.0/24'},
                         {'id': 'mysubid2', 'cidr': '172.16.0.0/24'},
                         {'id': 'mysubid3', 'cidr': '10.1.1.0/24'}],
                        query='fields=id&fields=cidr' + filters)
        self.mox.ReplayAll()

        args = []
        cmd_parser = cmd.get_parser('list_networks')
        parsed_args = cmd_parser.parse_args(args)
        result = cmd.get_data(parsed_args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _result = [x for x in result[1]]
        self.assertEqual(len(_result), len(expected))
        for res, exp in zip(_result, expected):
            self.assertEqual(len(res), len(exp))
            for a, b in zip(res, exp):
                self.assertEqual(a, b)

    def test_list_nets_extend_subnets(self):
        data = [{'id': 'netid1', 'name': 'net1', 'subnets': ['mysubid1']},
                {'id': 'netid2', 'name': 'net2', 'subnets': ['mysubid2',
                                                             'mysubid3']}]
        #             id,   name,   subnets
        expected = [('netid1', 'net1', 'mysubid1 192.168.1.0/24'),
                    ('netid2', 'net2',
                     'mysubid2 172.16.0.0/24\nmysubid3 10.1.1.0/24')]
        self._test_list_nets_extend_subnets(data, expected)

    def test_list_nets_extend_subnets_no_subnet(self):
        data = [{'id': 'netid1', 'name': 'net1', 'subnets': ['mysubid1']},
                {'id': 'netid2', 'name': 'net2', 'subnets': ['mysubid4']}]
        #             id,   name,   subnets
        expected = [('netid1', 'net1', 'mysubid1 192.168.1.0/24'),
                    ('netid2', 'net2', 'mysubid4 ')]
        self._test_list_nets_extend_subnets(data, expected)

    def test_list_nets_fields(self):
        """List nets: --fields a --fields b -- --fields c d."""
        resources = "networks"
        cmd = ListNetwork(MyApp(sys.stdout), None)
        self._test_list_networks(cmd,
                                 fields_1=['a', 'b'], fields_2=['c', 'd'])

    def _test_list_nets_columns(self, cmd, returned_body,
                                args=['-f', 'json']):
        resources = 'networks'
        self.mox.StubOutWithMock(ListNetwork, "extend_list")
        ListNetwork.extend_list(IsA(list), IgnoreArg())
        self._test_list_columns(cmd, resources, returned_body, args=args)

    def test_list_nets_defined_column(self):
        cmd = ListNetwork(MyApp(sys.stdout), None)
        returned_body = {"networks": [{"name": "buildname3",
                                       "id": "id3",
                                       "tenant_id": "tenant_3",
                                       "subnets": []}]}
        self._test_list_nets_columns(cmd, returned_body,
                                     args=['-f', 'json', '-c', 'id'])
        _str = self.fake_stdout.make_string()
        returned_networks = utils.loads(_str)
        self.assertEquals(1, len(returned_networks))
        network = returned_networks[0]
        self.assertEquals(1, len(network))
        self.assertEquals("id", network.keys()[0])

    def test_list_nets_with_default_column(self):
        cmd = ListNetwork(MyApp(sys.stdout), None)
        returned_body = {"networks": [{"name": "buildname3",
                                       "id": "id3",
                                       "tenant_id": "tenant_3",
                                       "subnets": []}]}
        self._test_list_nets_columns(cmd, returned_body)
        _str = self.fake_stdout.make_string()
        returned_networks = utils.loads(_str)
        self.assertEquals(1, len(returned_networks))
        network = returned_networks[0]
        self.assertEquals(3, len(network))
        self.assertEquals(0, len(set(network) ^
                                 set(cmd.list_columns)))

    def test_list_external_nets_empty_with_column(self):
        resources = "networks"
        cmd = ListExternalNetwork(MyApp(sys.stdout), None)
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        self.mox.StubOutWithMock(ListNetwork, "extend_list")
        ListNetwork.extend_list(IsA(list), IgnoreArg())
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        reses = {resources: []}
        resstr = self.client.serialize(reses)
        # url method body
        query = "router%3Aexternal=True&id=myfakeid"
        args = ['-c', 'id', '--', '--id', 'myfakeid']
        path = getattr(self.client, resources + "_path")
        self.client.httpclient.request(
            test_cli20.end_url(path, query), 'GET',
            body=None,
            headers=test_cli20.ContainsKeyValue(
                'X-Auth-Token',
                test_cli20.TOKEN)).AndReturn(
                    (test_cli20.MyResp(200), resstr))
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("list_" + resources)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        self.assertEquals('\n', _str)

    def _test_list_external_nets(self, resources, cmd,
                                 detail=False, tags=[],
                                 fields_1=[], fields_2=[]):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        self.mox.StubOutWithMock(ListNetwork, "extend_list")
        ListNetwork.extend_list(IsA(list), IgnoreArg())
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        reses = {resources: [{'id': 'myid1', },
                             {'id': 'myid2', }, ], }

        resstr = self.client.serialize(reses)

        # url method body
        query = ""
        args = detail and ['-D', ] or []
        if fields_1:
            for field in fields_1:
                args.append('--fields')
                args.append(field)
        if tags:
            args.append('--')
            args.append("--tag")
        for tag in tags:
            args.append(tag)
        if (not tags) and fields_2:
            args.append('--')
        if fields_2:
            args.append("--fields")
            for field in fields_2:
                args.append(field)
        fields_1.extend(fields_2)
        for field in fields_1:
            if query:
                query += "&fields=" + field
            else:
                query = "fields=" + field
        if query:
            query += '&router%3Aexternal=True'
        else:
            query += 'router%3Aexternal=True'
        for tag in tags:
            if query:
                query += "&tag=" + tag
            else:
                query = "tag=" + tag
        if detail:
            query = query and query + '&verbose=True' or 'verbose=True'
        path = getattr(self.client, resources + "_path")

        self.client.httpclient.request(
            test_cli20.end_url(path, query), 'GET',
            body=None,
            headers=ContainsKeyValue('X-Auth-Token',
                                     test_cli20.TOKEN)).AndReturn(
                                    (test_cli20.MyResp(200), resstr))
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("list_" + resources)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()

        self.assertTrue('myid1' in _str)

    def test_list_external_nets_detail(self):
        """list external nets: -D."""
        resources = "networks"
        cmd = ListExternalNetwork(MyApp(sys.stdout), None)
        self._test_list_external_nets(resources, cmd, True)

    def test_list_external_nets_tags(self):
        """List external nets: -- --tags a b."""
        resources = "networks"
        cmd = ListExternalNetwork(MyApp(sys.stdout), None)
        self._test_list_external_nets(resources,
                                      cmd, tags=['a', 'b'])

    def test_list_external_nets_detail_tags(self):
        """List external nets: -D -- --tags a b."""
        resources = "networks"
        cmd = ListExternalNetwork(MyApp(sys.stdout), None)
        self._test_list_external_nets(resources, cmd,
                                      detail=True, tags=['a', 'b'])

    def test_list_externel_nets_fields(self):
        """List external nets: --fields a --fields b -- --fields c d."""
        resources = "networks"
        cmd = ListExternalNetwork(MyApp(sys.stdout), None)
        self._test_list_external_nets(resources, cmd,
                                      fields_1=['a', 'b'],
                                      fields_2=['c', 'd'])

    def test_update_network_exception(self):
        """Update net: myid."""
        resource = 'network'
        cmd = UpdateNetwork(MyApp(sys.stdout), None)
        self.assertRaises(exceptions.CommandError, self._test_update_resource,
                          resource, cmd, 'myid', ['myid'], {})

    def test_update_network(self):
        """Update net: myid --name myname --tags a b."""
        resource = 'network'
        cmd = UpdateNetwork(MyApp(sys.stdout), None)
        self._test_update_resource(resource, cmd, 'myid',
                                   ['myid', '--name', 'myname',
                                    '--tags', 'a', 'b'],
                                   {'name': 'myname', 'tags': ['a', 'b'], }
                                   )

    def test_show_network(self):
        """Show net: --fields id --fields name myid."""
        resource = 'network'
        cmd = ShowNetwork(MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id, args,
                                 ['id', 'name'])

    def test_delete_network(self):
        """Delete net: myid."""
        resource = 'network'
        cmd = DeleteNetwork(MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)
