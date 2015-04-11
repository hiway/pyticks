#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 jaidev <jaidev@newton>
#
# Distributed under terms of the MIT license.

"""Tests."""


import json
import os.path as op
import unittest
import responses
import pyticks


class TestPyTicks(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.engine = pyticks.PyTicks()
        self.url = pyticks.URL.format(username="jaidevd", repo="pyticks")
        self.issue1_body = json.dumps(dict(
                      body="this is the body of the dummy issue.",
                      title="this is a dummy issue"))
        self.issue2_body = json.dumps(dict(
                      body="this is the body of the second issue.",
                      title="this is another issue"))

    def test_get_toplevel_dir(self):
        """Check if the toplevel directory is detected correctly."""
        ideal = op.abspath(op.dirname(__file__))
        self.assertEqual(self.engine.working_dir, ideal)

    def test_find_files(self):
        ideal = ['tests.py', 'pyticks.py', 'cli.py', 'README.md', '.gitignore',
                 'requirements.txt', 'setup.py', 'LICENSE']
        ideal = [op.join(op.abspath(op.dirname(__file__)), f) for f in ideal]
        self.assertItemsEqual(ideal, self.engine.files)

    def test_find_fixme(self):
        # FIXME: this is a dummy issue
        # this is the body of the dummy issue.

        # FIXME: this is another issue
        # this is the body of the second issue.
        fixmes = self.engine._find_fixme(__file__)
        self.assertEqual(len(fixmes), 2)
        ideal = [json.loads(self.issue1_body), json.loads(self.issue2_body)]
        for i in range(2):
            issue = ideal[i]
            self.assertEqual(issue['title'], fixmes[i]['title'])
            self.assertEqual(issue['body'], fixmes[i]['body'])

    @responses.activate
    def test_report_issue(self):
        responses.add(responses.POST, self.url, status=201,
                      body=self.issue1_body, content_type="application/json")
        resps = self.engine.run()
        self.assertEqual(len(resps), 2)
        for resp in resps:
            self.assertEqual(resp.calls[0].url, self.url)
        self.assertEqual(resps[0].response.text, self.issue1_body)
        self.assertEqual(resps[1].response.text, self.issue2_body)

if __name__ == '__main__':
    unittest.main()