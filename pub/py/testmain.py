'''
Copyright 2016 ASAP.

Licensed to the Apache Software Foundation (ASF) under one or more
contributor license agreements.  See the NOTICE file distributed with
this work for additional information regarding copyright ownership.
The ASF licenses this file to You under the Apache License, Version 2.0
(the "License"); you may not use this file except in compliance with
the License.  You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

#!/usr/bin/env python
import sys, os
import unittest
import main
from datetime import datetime
import shutil

class TestWorkflow(unittest.TestCase):

    def setUp(self):
        self.workflow = main.Workflow('testwl.json')

    def tearDown(self):
        self.workflow = None

    def test_analyse(self):
        self.workflow.analyse()
        self.workflow_a = main.Workflow('testwl-a.json')
        self.assertEqual(self.workflow, self.workflow_a)

    def test_save(self):
        self.workflow.WLibrary = './'
        current_time = datetime.now().strftime("%Y-%m-%d_%H:%M")
        self.workflow.save()
        self.assertTrue(os.path.isfile(self.workflow.name + '_' + current_time))
        os.remove(self.workflow.name + '_' + current_time)

    def test_execute(self):
        self.workflow.analyse()
        self.workflow.WLibrary = './'
        current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%s")
        self.workflow.execute()
        self.assertTrue(os.path.isdir(self.workflow.name + '_' + current_time))
        shutil.rmtree(self.workflow.name + '_' + current_time)

    def test_findNode(self):
        self.assertEqual(self.workflow.findNode(1)['id'], 1)

    def test_findTask(self):
        self.assertEqual(self.workflow.findTask(1)['id'], 1)

    def test_findEdge(self):
        self.assertEqual(self.workflow.findEdge(1)['id'], 1)

    def test_dict2text(self):
        sin = {
            "constraints": {
                "input": {"number": 1},
                "output": {"number": 1},
                "opSpecification": {
                    "algorithm": {"name": "Wind_Data_Filter"}
                }
            }
        }
        sout1 = ''
        for d in main.dict2text(sin):
            sout1 = sout1 + d + '\n'
        sout2 = "constraints.input.number=1\n" \
               "constraints.opSpecification.algorithm.name=Wind_Data_Filter\n" \
               "constraints.output.number=1\n"
        self.assertEqual(sout1, sout2)

if __name__ == '__main__':
    unittest.main()