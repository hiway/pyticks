#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 jaidev <jaidev@newton>
#
# Distributed under terms of the MIT license.

"""Tests."""

import os
import os.path as op
import shutil
import unittest
import git


class TestBase(unittest.TestCase):
    """Base class for all test cases. Sets up the metadata required for the
    tests."""

    @classmethod
    def setUpClass(cls):
        cls.testrepo_location = op.join(op.abspath(op.dirname(__file__)),
                                        "testdata", "testrepo")

        # move the sample.pyticksrc file to the correct location
        sample_pyticksrc_org = op.join(op.dirname(__file__), "testdata",
                                       "sample.pyticksrc")
        cls.sample_pyticksrc_dest = op.join(cls.testrepo_location, ".pyticksrc")
        shutil.copyfile(sample_pyticksrc_org, cls.sample_pyticksrc_dest)

        # stage some files
        cls.repo = git.Repo.init(cls.testrepo_location)
        cls.repo.index.add([op.join(cls.testrepo_location, "file1.py")])
        cls.repo.index.add([op.join(cls.testrepo_location, "file2.md")])
        cls.repo.index.add([op.join(cls.testrepo_location, ".pyticksrc")])
        cls.repo.index.commit("Initial commit.")

    @classmethod
    def tearDownClass(cls):
        # De-init the git repo
        shutil.rmtree(op.join(cls.testrepo_location, ".git"))
        # remove sample .pyticksrc
        os.unlink(cls.sample_pyticksrc_dest)


class TestPyticks(TestBase):

    def test_untracked(self):
        """Test if untracked files are found properly."""
        self.assertEqual(len(self.repo.untracked_files), 1)
        self.assertIn("untracked_file.py", self.repo.untracked_files)


# class TestConfig(unittest.TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         cls.tld = tempfile.mkdtemp()
#         cls.repo = Repo.init(cls.tld)
#         cls.testdata = op.join(op.abspath(op.dirname(__file__)), "testdata")
#         org_location = op.join(cls.testdata, ".pyticksrc")
#         new_location = op.join(cls.tld, ".pyticksrc")
#         shutil.copy(org_location, new_location)
#
#     def test_get_config_file(self):
#         ideal = op.join(self.tld, ".pyticksrc")
#         actual = pyticks.locate_config_file(self.tld)
#         self.assertEqual(ideal, actual)
#
#     @classmethod
#     def tearDownClass(cls):
#         shutil.rmtree(cls.tld)
#
#
# class TestPyTicks(unittest.TestCase):
#
#     def setUp(self):
#         test_netrc_path = op.join(op.abspath(op.dirname(__file__)), "testdata",
#                                   "sample.netrc")
#         os.environ['PYTICKS_NETRC'] = test_netrc_path
#         self.maxDiff = None
#         self.engine = pyticks.PyTicks()
#         self.url = pyticks.URL.format(orgname="jaidevd", repo="pyticks")
#         self.issue1_body = json.dumps(dict(
#                       body='this is the body of the dummy issue.',
#                       title='this is a dummy issue'))
#         self.issue2_body = json.dumps(dict(
#                       body='this is the body of the second issue.',
#                       title='this is another issue'))
#         self.cache_location = op.join(op.expanduser("~"), ".pyticks", "cache.json")
#
#     def tearDown(self):
#         del os.environ['PYTICKS_NETRC']
#
#     def _backup_cache(self, undo=False):
#         if not undo:
#             shutil.copy(self.cache_location, self.cache_location + ".1")
#         else:
#             shutil.move(self.cache_location + ".1", self.cache_location)
#
#     def test_get_toplevel_dir(self):
#         """Check if the toplevel directory is detected correctly."""
#         ideal = op.abspath(op.dirname(__file__))
#         self.assertEqual(self.engine.working_dir, ideal)
#
#     def test_find_files(self):
#         ideal = subprocess.check_output("git ls-files".split(),
#                                         cwd=op.abspath(op.dirname(__file__)))
#         ideal = ideal.splitlines()
#         ideal = [op.join(op.abspath(op.dirname(__file__)), f) for f in ideal]
#         ideal = [f for f in ideal if f.endswith(".py")]
#         self.assertItemsEqual(ideal, self.engine.files)
#
#     def test_find_fixme(self):
#         # FIXME: this is a dummy issue
#         # this is the body of the dummy issue.
#
#         # FIXME: this is another issue
#         # this is the body of the second issue.
#         fixmes = self.engine._find_fixme(__file__)
#         self.assertEqual(len(fixmes), 2)
#         ideal = [json.loads(self.issue1_body), json.loads(self.issue2_body)]
#         for i in range(2):
#             issue = ideal[i]
#             self.assertEqual(issue["title"], fixmes[i]["title"])
#             self.assertEqual(issue["body"], fixmes[i]["body"])
#
#     def test_auth(self):
#         """Test if correct credentials are found in netrc."""
#         username, password = self.engine.get_netrc_auth()
#         self.assertEqual(username, "jaidevd")
#         self.assertEqual(password, "password")
#
#     def test_get_cache(self):
#         """Check if the correct location of the cache is returned."""
#         actual = self.engine.get_cache()
#         self.assertEqual(self.cache_location, actual)
#
#     def test_clear_cache(self):
#         self.engine.encache(self.issue1_body)
#         self.engine.encache(self.issue1_body)
#         self._backup_cache()
#         ideal = op.join(os.expanduser("~"), ".pyticks", "cache.json")
#         try:
#             self.engine.clear_cache()
#             with open(ideal, "r") as fin:
#                 self.assertEqual(fin.read().rstrip(), '{}')
#         finally:
#             self._backup_cache(undo=True)
#
#     @responses.activate
#     def test_cache(self):
#         responses.add(responses.POST, self.url, status=201,
#                       body=self.issue1_body, content_type="application/json")
#         self.engine.run()
#         cache = self.engine.get_cache()
#         try:
#             self.assertIn("pyticks", cache)
#             issues = cache['pyticks']
#             self.assertIn(self.issue1_body, issues)
#             self.assertIn(self.issue2_body, issues)
#         finally:
#             self.engine.clear_cache()
#
#     @responses.activate
#     def test_report_issue(self):
#         responses.add(responses.POST, self.url, status=201,
#                       body=self.issue1_body, content_type="application/json")
#         resps = self.engine.run()
#         self.assertEqual(len(resps), 2)
#         self.assertEqual(responses.calls[0].request.url, self.url)
#         self.assertEqual(responses.calls[1].request.url, self.url)
#         self.assertEqual(ast.literal_eval(resps[0].text),
#                          ast.literal_eval(self.issue1_body))

if __name__ == "__main__":
    unittest.main()
