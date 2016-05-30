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

    # preparing to test
    # loading workflow form testwl.json
    def setUp(self):
        self.workflow = main.Workflow('testwl.json')

    # ending the test
    def tearDown(self):
        self.workflow = None

    # testing of analyse function through comparison of its result with the presaved result in a file testwl-a.json
    def test_analyse(self):
        self.workflow.analyse()
        self.workflow_a = main.Workflow('testwl-a.json')
        self.assertEqual(self.workflow.__repr__(), self.workflow_a.__repr__())

    # checking that save function generates a file with correct name
    def test_save(self):
        self.workflow.WLibrary = './'
        current_time = datetime.now().strftime("%Y-%m-%d_%H:%M")
        self.workflow.save()
        self.assertTrue(os.path.isfile(self.workflow.name + '_' + current_time))
        os.remove(self.workflow.name + '_' + current_time)

    # checking that execute function saves a workflow in IReS format (correct folder and presence of required files in it)
    # TODO: check that yarn task is running
    def test_execute(self):
        self.workflow.analyse()
        self.workflow.WLibrary = './'
        current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%s")
        self.workflow.execute()
        self.assertTrue(os.path.isdir(self.workflow.name + '_' + current_time))
        self.assertTrue(os.path.isfile(os.path.join(self.workflow.name + '_' + current_time, 'graph')))
        self.assertTrue(os.path.isdir(os.path.join(self.workflow.name + '_' + current_time, 'datasets')))
        self.assertTrue(os.path.isdir(os.path.join(self.workflow.name + '_' + current_time, 'operators')))
        shutil.rmtree(self.workflow.name + '_' + current_time)

    # checking that found node with findNode function has correct id
    def test_findNode(self):
        self.assertEqual(self.workflow.findNode(1)['id'], 1)

    # checking that found task with findTask function has correct id
    def test_findTask(self):
        self.assertEqual(self.workflow.findTask(1)['id'], 1)

    # checking that found edge with findEdge function has correct id
    def test_findEdge(self):
        self.assertEqual(self.workflow.findEdge(1)['id'], 1)

    # testing inner function dict2text through comparison of its result with the presaved result
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