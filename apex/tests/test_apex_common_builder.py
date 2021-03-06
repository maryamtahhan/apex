##############################################################################
# Copyright (c) 2017 Tim Rozet (Red Hat)
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import unittest

from apex.builders import common_builder as c_builder
from apex.common import constants as con
from mock import patch
from mock import mock_open
from mock import MagicMock


class TestCommonBuilder(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        """This method is run once for each class before any tests are run"""

    @classmethod
    def teardown_class(cls):
        """This method is run once for each class _after_ all tests are run"""

    def setup(self):
        """This method is run once before _each_ test method is executed"""

    def teardown(self):
        """This method is run once after _each_ test method is executed"""

    def test_project_to_path(self):
        project = 'openstack/tripleo-heat-templates'
        path = '/usr/share/openstack-tripleo-heat-templates'
        self.assertEquals(c_builder.project_to_path(project), path)
        project = 'openstack/puppet-tripleo'
        path = '/etc/puppet/modules/tripleo'
        self.assertEquals(c_builder.project_to_path(project), path)
        project = 'openstack/nova'
        path = '/usr/lib/python2.7/site-packages/nova'
        self.assertEquals(c_builder.project_to_path(project), path)

    @patch('builtins.open', mock_open())
    @patch('apex.build_utils.get_patch')
    @patch('apex.virtual.utils.virt_customize')
    def test_add_upstream_patches(self, mock_customize, mock_get_patch):
        mock_get_patch.return_value = None
        change_id = 'I301370fbf47a71291614dd60e4c64adc7b5ebb42'
        patches = [{
            'change-id': change_id,
            'project': 'openstack/tripleo-heat-templates'
        }]
        c_builder.add_upstream_patches(patches, 'dummy.qcow2', '/dummytmp/')
        assert mock_customize.not_called
        project_path = '/usr/share/openstack-tripleo-heat-templates'
        patch_file = "{}.patch".format(change_id)
        patch_file_path = "/dummytmp/{}".format(patch_file)
        test_virt_ops = [
            {con.VIRT_INSTALL: 'patch'},
            {con.VIRT_UPLOAD: "{}:{}".format(patch_file_path,
                                             project_path)},
            {con.VIRT_RUN_CMD: "cd {} && patch -p1 < {}".format(
                project_path, patch_file)}]
        mock_get_patch.return_value = 'some random diff'
        c_builder.add_upstream_patches(patches, 'dummy.qcow2', '/dummytmp/')
        mock_customize.assert_called_once_with(test_virt_ops, 'dummy.qcow2')

    @patch('builtins.open', mock_open())
    @patch('apex.virtual.utils.virt_customize')
    def test_add_repo(self, mock_customize):
        c_builder.add_repo('fake/url', 'dummyrepo', 'dummy.qcow2',
                           '/dummytmp/')
        repo_file_path = '/dummytmp/dummyrepo.repo'
        test_virt_ops = [
            {con.VIRT_UPLOAD: "{}:/etc/yum.repos.d/".format(repo_file_path)}
        ]
        mock_customize.assert_called_once_with(test_virt_ops, 'dummy.qcow2')

    @patch('builtins.open', mock_open())
    @patch('git.Repo.clone_from')
    def test_create_git_archive(self, mock_git):
        mock_git.return_value = MagicMock()
        self.assertEqual(c_builder.create_git_archive('fake/url', 'dummyrepo',
                                                      '/dummytmp/'),
                         '/dummytmp/dummyrepo.tar')
