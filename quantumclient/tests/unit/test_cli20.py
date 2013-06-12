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

import fixtures
import mox
from mox import Comparator
from mox import ContainsKeyValue
import testtools

from quantumclient import shell
from quantumclient.v2_0.client import Client


API_VERSION = "2.0"
FORMAT = 'json'
TOKEN = 'testtoken'
ENDURL = 'localurl'


class FakeStdout:

    def __init__(self):
        self.content = []

    def write(self, text):
        self.content.append(text)

    def make_string(self):
        result = ''
        for line in self.content:
            result = result + line
        return result


class MyResp(object):
    def __init__(self, status):
        self.status = status


class MyApp(object):
    def __init__(self, _stdout):
        self.stdout = _stdout


def end_url(path, query=None):
    _url_str = ENDURL + "/v" + API_VERSION + path + "." + FORMAT
    return query and _url_str + "?" + query or _url_str


class MyUrlComparator(Comparator):
    def __init__(self, lhs, client):
        self.lhs = lhs
        self.client = client

    def equals(self, rhs):
        return str(self) == rhs

    def __str__(self):
        if self.client and self.client.format != FORMAT:
            lhs_parts = self.lhs.split("?", 1)
            if len(lhs_parts) == 2:
                lhs = ("%s%s?%s" % (lhs_parts[0][:-4],
                                    self.client.format,
                                    lhs_parts[1]))
            else:
                lhs = ("%s%s" % (lhs_parts[0][:-4],
                                 self.client.format))
            return lhs
        return self.lhs

    def __repr__(self):
        return str(self)


class MyComparator(Comparator):
    def __init__(self, lhs, client):
        self.lhs = lhs
        self.client = client

    def _com_dict(self, lhs, rhs):
        if len(lhs) != len(rhs):
            return False
        for key, value in lhs.iteritems():
            if key not in rhs:
                return False
            rhs_value = rhs[key]
            if not self._com(value, rhs_value):
                return False
        return True

    def _com_list(self, lhs, rhs):
        if len(lhs) != len(rhs):
            return False
        for lhs_value in lhs:
            if lhs_value not in rhs:
                return False
        return True

    def _com(self, lhs, rhs):
        if lhs is None:
            return rhs is None
        if isinstance(lhs, dict):
            if not isinstance(rhs, dict):
                return False
            return self._com_dict(lhs, rhs)
        if isinstance(lhs, list):
            if not isinstance(rhs, list):
                return False
            return self._com_list(lhs, rhs)
        if isinstance(lhs, tuple):
            if not isinstance(rhs, tuple):
                return False
            return self._com_list(lhs, rhs)
        return lhs == rhs

    def equals(self, rhs):
        if self.client:
            rhs = self.client.deserialize(rhs, 200)
        return self._com(self.lhs, rhs)

    def __repr__(self):
        return str(self.lhs)


class CLITestV20Base(testtools.TestCase):

    test_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'

    def _find_resourceid(self, client, resource, name_or_id):
        return name_or_id

    def setUp(self):
        """Prepare the test environment"""
        super(CLITestV20Base, self).setUp()
        self.mox = mox.Mox()
        self.endurl = ENDURL
        self.client = Client(token=TOKEN, endpoint_url=self.endurl)
        self.fake_stdout = FakeStdout()
        self.useFixture(fixtures.MonkeyPatch('sys.stdout', self.fake_stdout))
        self.useFixture(fixtures.MonkeyPatch(
            'quantumclient.quantum.v2_0.find_resourceid_by_name_or_id',
            self._find_resourceid))

    def _test_create_resource(self, resource, cmd,
                              name, myid, args,
                              position_names, position_values, tenant_id=None,
                              tags=None, admin_state_up=True, shared=False,
                              extra_body=None, **kwargs):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        non_admin_status_resources = ['subnet', 'floatingip', 'security_group',
                                      'security_group_rule', 'qos_queue',
                                      'network_gateway']
        if (resource in non_admin_status_resources):
            body = {resource: {}, }
        else:
            body = {resource: {'admin_state_up': admin_state_up, }, }
        if tenant_id:
            body[resource].update({'tenant_id': tenant_id})
        if tags:
            body[resource].update({'tags': tags})
        if shared:
            body[resource].update({'shared': shared})
        if extra_body:
            body[resource].update(extra_body)
        body[resource].update(kwargs)

        for i in xrange(len(position_names)):
            body[resource].update({position_names[i]: position_values[i]})
        ress = {resource:
                {'id': myid}, }
        if name:
            ress[resource].update({'name': name})
        resstr = self.client.serialize(ress)
        # url method body
        path = getattr(self.client, resource + "s_path")
        self.client.httpclient.request(
            end_url(path), 'POST',
            body=MyComparator(body, self.client),
            headers=ContainsKeyValue('X-Auth-Token',
                                     TOKEN)).AndReturn((MyResp(200),
                                                        resstr))
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser('create_' + resource)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        self.assertTrue(myid in _str)
        if name:
            self.assertTrue(name in _str)

    def _test_list_columns(self, cmd, resources_collection,
                           resources_out, args=['-f', 'json']):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        resstr = self.client.serialize(resources_out)

        path = getattr(self.client, resources_collection + "_path")
        self.client.httpclient.request(
            end_url(path), 'GET',
            body=None,
            headers=ContainsKeyValue('X-Auth-Token',
                                     TOKEN)).AndReturn((MyResp(200), resstr))
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("list_" + resources_collection)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()

    def _test_list_resources(self, resources, cmd, detail=False, tags=[],
                             fields_1=[], fields_2=[], page_size=None,
                             sort_key=[], sort_dir=[]):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
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
            if query:
                query += "&tag=" + tag
            else:
                query = "tag=" + tag
            args.append(tag)
        if (not tags) and fields_2:
            args.append('--')
        if fields_2:
            args.append("--fields")
            for field in fields_2:
                args.append(field)
        if detail:
            query = query and query + '&verbose=True' or 'verbose=True'
        fields_1.extend(fields_2)
        for field in fields_1:
            if query:
                query += "&fields=" + field
            else:
                query = "fields=" + field
        if page_size:
            args.append("--page-size")
            args.append(str(page_size))
            if query:
                query += "&limit=%s" % page_size
            else:
                query = "limit=%s" % page_size
        if sort_key:
            for key in sort_key:
                args.append('--sort-key')
                args.append(key)
                if query:
                    query += '&'
                query += 'sort_key=%s' % key
        if sort_dir:
            len_diff = len(sort_key) - len(sort_dir)
            if len_diff > 0:
                sort_dir += ['asc'] * len_diff
            elif len_diff < 0:
                sort_dir = sort_dir[:len(sort_key)]
            for dir in sort_dir:
                args.append('--sort-dir')
                args.append(dir)
                if query:
                    query += '&'
                query += 'sort_dir=%s' % dir
        path = getattr(self.client, resources + "_path")
        self.client.httpclient.request(
            MyUrlComparator(end_url(path, query), self.client), 'GET',
            body=None,
            headers=ContainsKeyValue('X-Auth-Token',
                                     TOKEN)).AndReturn((MyResp(200), resstr))
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("list_" + resources)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        self.assertTrue('myid1' in _str)

    def _test_list_resources_with_pagination(self, resources, cmd):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        path = getattr(self.client, resources + "_path")
        fake_query = "marker=myid2&limit=2"
        reses1 = {resources: [{'id': 'myid1', },
                              {'id': 'myid2', }],
                  '%s_links' % resources: [{'href': end_url(path, fake_query),
                                            'rel': 'next'}]}
        reses2 = {resources: [{'id': 'myid3', },
                              {'id': 'myid4', }]}
        resstr1 = self.client.serialize(reses1)
        resstr2 = self.client.serialize(reses2)
        self.client.httpclient.request(
            end_url(path, ""), 'GET',
            body=None,
            headers=ContainsKeyValue('X-Auth-Token',
                                     TOKEN)).AndReturn((MyResp(200), resstr1))
        self.client.httpclient.request(
            end_url(path, fake_query), 'GET',
            body=None,
            headers=ContainsKeyValue('X-Auth-Token',
                                     TOKEN)).AndReturn((MyResp(200), resstr2))
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("list_" + resources)

        parsed_args = cmd_parser.parse_args("")
        cmd.run(parsed_args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()

    def _test_update_resource(self, resource, cmd, myid, args, extrafields):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        body = {resource: extrafields}
        path = getattr(self.client, resource + "_path")
        self.client.httpclient.request(
            MyUrlComparator(end_url(path % myid), self.client), 'PUT',
            body=MyComparator(body, self.client),
            headers=ContainsKeyValue('X-Auth-Token',
                                     TOKEN)).AndReturn((MyResp(204), None))
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("update_" + resource)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        self.assertTrue(myid in _str)

    def _test_show_resource(self, resource, cmd, myid, args, fields=[]):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        query = "&".join(["fields=%s" % field for field in fields])
        expected_res = {resource:
                        {'id': myid,
                        'name': 'myname', }, }
        resstr = self.client.serialize(expected_res)
        path = getattr(self.client, resource + "_path")
        self.client.httpclient.request(
            end_url(path % myid, query), 'GET',
            body=None,
            headers=ContainsKeyValue('X-Auth-Token',
                                     TOKEN)).AndReturn((MyResp(200), resstr))
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("show_" + resource)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        self.assertTrue(myid in _str)
        self.assertTrue('myname' in _str)

    def _test_delete_resource(self, resource, cmd, myid, args):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        path = getattr(self.client, resource + "_path")
        self.client.httpclient.request(
            end_url(path % myid), 'DELETE',
            body=None,
            headers=ContainsKeyValue('X-Auth-Token',
                                     TOKEN)).AndReturn((MyResp(204), None))
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("delete_" + resource)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        self.assertTrue(myid in _str)

    def _test_update_resource_action(self, resource, cmd, myid, action, args,
                                     body):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        path = getattr(self.client, resource + "_path")
        path_action = '%s/%s' % (myid, action)
        self.client.httpclient.request(
            end_url(path % path_action), 'PUT',
            body=MyComparator(body, self.client),
            headers=ContainsKeyValue('X-Auth-Token',
                                     TOKEN)).AndReturn((MyResp(204), None))
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser("delete_" + resource)
        shell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        self.assertTrue(myid in _str)
