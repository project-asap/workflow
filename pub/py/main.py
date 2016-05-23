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
import ruamel.yaml as yaml
import copy
import json
from datetime import datetime


class Workflow:

    WLibrary = '../workflows/'

    def __init__(self, fname):
        if not os.path.exists(fname):
            print 'ERROR: File '+fname+' was not found!'
            sys.exit(0)
        fl = open(fname, 'r')
        wl = yaml.safe_load(fl)
        fl.close()
        self.name = wl['name'] if 'name' in wl else 'workflow'
        self.nodes = wl['nodes'] if 'nodes' in wl else []
        self.edges = wl['edges'] if 'edges' in wl else []
        self.tasks = wl['tasks'] if 'tasks' in wl else []
        self.taskLinks = wl['taskLinks'] if 'taskLinks' in wl else []

    def __repr__(self):
        return json.dumps({
            'name': self.name,
            'nodes': self.nodes,
            'edges': self.edges,
            'tasks': self.tasks,
            'taskLinks': self.taskLinks
        }, sort_keys=True, indent=2)

    def analyse(self):
        for node in self.nodes:
            node['predecessors'] = []
            node['successors'] = []
            node['taskIds'] = []
        for task in self.tasks:
            nid = task['nodeId']
            node = self.findNode(nid)
            if task['id'] not in node['taskIds']:
                node['taskIds'].append(task['id'])
        for edge in self.edges:
            inp = edge['sourceId']
            out = edge['targetId']
            nodeI = self.findNode(inp)
            nodeJ = self.findNode(out)
            if out not in nodeI['successors']:
                nodeI['successors'].append(out)
            if inp not in nodeJ['predecessors']:
                nodeJ['predecessors'].append(inp)
        # Checking for cycle (TODO: optimise it)

        def retSuccessors(self, nIds):
            sucs = []
            for nId in nIds:
                for suc in self.findNode(nId)['successors']:
                    if suc not in sucs:
                        sucs.append(suc)
            return sucs

        for node in self.nodes:
            nId = node['id']
            nIds = [nId]
            iter = 0
            while len(nIds) != 0 and iter < 5:
                nIds = retSuccessors(self, nIds)
                if nId in nIds:
                    print 'ERROR: Workflow contains a cycle!'
                    sys.exit(0)
                iter += 1
        # Splitting multi-task vertices
        for node in self.nodes:
            if len(node['taskIds']) == 0:
                print 'ERROR: Node '+node['name']+' has no tasks inside!'
                sys.exit(0)
            if len(node['taskIds']) > 1:
                if self.isNodeBranching(node['id']):
                    print 'ERROR: Splitting of branching node '+node['name']+' is not supported yet!'
                    sys.exit(0)
                tList = [node['taskIds'][0]]
                for tId in node['taskIds']:
                    task = self.findTask(tId)
                    if 'schema' not in task['operator'].keys() or 'input' not in task['operator']['schema'].keys() or 'output' not in task['operator']['schema'].keys():
                        print 'ERROR: Task '+task['name']+' hasn\'t schema description, splitting can\'t be performed'
                        sys.exit(0)
                    if tId in tList:
                        continue
                    if set(task['operator']['schema']['output']) == set(self.findTask(tList[0])['operator']['schema']['input']):
                        tList = [tId] + tList
                    if set(task['operator']['schema']['input']) == set(self.findTask(tList[-1])['operator']['schema']['output']):
                        tList.append(tId)
                if len(tList) != len(node['taskIds']):
                    print 'ERROR: Splitting wasn\'t performed!'
                    sys.exit(0)
                node['taskIds'] = [tList[0]]
                node['name'] = self.findTask(tList[0])['name']
                self.findTask(tList[0])['nodeId'] = node['id']
                nodePrev = node
                for edge in self.edges:
                    if edge['sourceId'] == nodePrev['id']:
                        eId = edge['id']
                        lId = edge['targetId']
                for tId in tList[1:]:
                    j = str(node['id'])+'0'+str(tId)
                    self.findTask(tId)['nodeId'] = j
                    cNode = {}
                    cNode['id'] = j
                    cNode['taskIds'] = [tId]
                    cNode['name'] = self.findTask(tId)['name']
                    cNode['predecessors'] = [nodePrev['id']]
                    cNode['successors'] = []
                    nodePrev['successors'] = [j]
                    self.nodes.append(cNode)
                    self.edges.append({
                        'id': str(eId)+'0'+str(nodePrev['id']),
                        'sourceId': nodePrev['id'],
                        'targetId': j
                    })
                    nodePrev = self.findNode(j)
                self.findEdge(eId)['sourceId'] = nodePrev['id']
                nodePrev['successors'] = [lId]
        # Augmentting the workflow with associative tasks
        for edge in self.edges:
            nodeI = self.findNode(edge['sourceId'])
            nodeJ = self.findNode(edge['targetId'])
            taskI = self.findTask(nodeI['taskIds'][0])
            taskJ = self.findTask(nodeJ['taskIds'][0])
            if 'operator' in taskI.keys() and 'engine' in taskI['operator'].keys() and 'fs' in taskI['operator']['engine'].keys() and 'operator' in taskJ.keys() and 'engine' in taskJ['operator'].keys() and 'fs' in taskJ['operator']['engine'].keys():
                if taskI['operator']['engine']['fs'] != taskJ['operator']['engine']['fs']:
                    nId = str(len(self.nodes))+str(1)
                    tId = str(len(self.tasks))+str(1)
                    self.nodes.append({
                        'id': nId,
                        'taskIds': [tId],
                        'name': 'format_conv',
                        'predecessors': [nodeI['id']],
                        'successors': [nodeJ['id']]
                    })
                    self.tasks.append({
                        'id': tId,
                        'name': 'format_conv',
                        'nodeId': nId,
                        'operator': {
                            'constraints': {
                                'input': 1,
                                'output': 1,
                                'opSpecification': {
                                    'algorithm': 'convert',
                                    'from': taskI['operator']['engine']['fs'],
                                    'to': taskJ['operator']['engine']['fs']
                                }
                            }
                          }
                    })
                    for edge in self.edges:
                        if edge['sourceId'] == nodeI['id'] and edge['targetId'] == nodeJ['id']:
                            edge['targetId'] = nId
                    self.edges.append({
                        'id': str(len(self.edges))+str(1),
                        'sourceId': nId,
                        'targetId': nodeJ['id']
                    })

    def optimise(self):
        moved = -1
        while moved != 0:
            moved = 0
            for edge in self.edges:
                i = edge['sourceId']
                j = edge['targetId']
                ni = self.findNode(i)
                nj = self.findNode(j)
                if self.isNodeUnary(i) and self.isNodeUnary(j) and len(ni['taskIds']) == 1 and len(nj['taskIds']) == 1:
                    ti = self.findTask(ni['taskIds'][0])
                    tj = self.findTask(nj['taskIds'][0])
                    if 'operator' in ti and 'constraints' in ti['operator'] or 'name' in ti['operator']['constraints'] and 'filter' in ti['operator']['constraints']['name'] and 'select' in ti['operator']['constraints']['name']:
                        continue
                    # heuristic 1
                    # move restrictive operators to the start
                    elif 'operator' in tj and 'constraints' in tj['operator'] or 'name' in tj['operator']['constraints'] and 'filter' in tj['operator']['constraints']['name'] and 'select' in tj['operator']['constraints']['name']:
                        ni['taskIds'][0] = tj['id']
                        ti['nodeId'] = int(nj['id'])
                        nj['taskIds'][0] = ti['id']
                        tj['nodeId'] = int(ni['id'])
                        moved += 1
                        # print ti
                        # print tj
                    elif 'operator' in ti and 'constraints' in ti['operator'] or 'name' in ti['operator']['constraints'] and 'calc' in ti['operator']['constraints']['name']:
                        continue
                    # heuristic 2
                    # place non-blocking operators together and separately from blocking operators
                    elif 'operator' in tj and 'constraints' in tj['operator'] or 'name' in tj['operator']['constraints'] and 'calc' in tj['operator']['constraints']['name']:
                        ni['taskIds'][0] = tj['id']
                        ti['nodeId'] = int(nj['id'])
                        nj['taskIds'][0] = ti['id']
                        tj['nodeId'] = int(ni['id'])
                        moved += 1
                        # print tinp
                        # print tout
                    else:
                        continue
                else:
                    continue
            # print moved

    def copy(self):
        return copy.deepcopy(self)

    def es(self):
        wmin = self.copy()
        open = [self]
        close = []

        HP = self.findHomologousNodes()

        while len(open) != 0:
            w = open.pop()
            # composing all possible pairs
            for edge in self.edges:
                inp = edge['sourceId']
                out = edge['targetId']
                wnew = w.compose(inp, out)
                if wnew not in open and wnew not in close:
                    if wnew.getCost() < wmin.getCost():
                        wmin = wnew.copy()
                    open.append(wnew)

            # swapping all possible pairs
            for edge in self.edges:
                inp = edge['sourceId']
                out = edge['targetId']
                w.swap(inp, out)
                if wnew not in open and wnew not in close:
                    if wnew.getCost() < wmin.getCost():
                        wmin = wnew.copy()
                    open.append(wnew)

            # factorizing all pairs of homologous nodes
            for pair in HP:
                inp = pair.first
                out = pair.second
                w.factorize(inp, out)
                if wnew not in open and wnew not in close:
                    if wnew.getCost() < wmin.getCost():
                        wmin = wnew.copy()
                    open.append(wnew)

            close.append(w)
        return wmin

    def hs(self):
        wmin = self.copy()
        open = [self]
        close = []

        HP = self.findHomologousNodes()
        LP = self.findLinearPaths()

        while len(open) != 0:
            w = open.pop()
            # composing all possible pairs
            for k in LP:
                edge = self.findEdge(k)
                inp = edge['sourceId']
                out = edge['targetId']
                wnew = w.compose(inp, out)
                if (wnew not in open and wnew not in close):
                    if wnew.getCost() < wmin.getCost():
                        wmin = wnew.copy()
                    open.append(wnew)

            # swapping all possible pairs
            for k in LP:
                edge = self.findEdge(k)
                inp = edge['sourceId']
                out = edge['targetId']
                w.swap(inp, out)
                if wnew not in open and wnew not in close:
                    if wnew.getCost() < wmin.getCost():
                        wmin = wnew.copy()
                    open.append(wnew)

            # factorizing all pairs of homologous nodes
            for pair in HP:
                i = pair.first
                j = pair.second
                nodeI = w.findNode(i)
                nodeJ = w.findNode(j)
                pred = list(set(nodeI['predecessors']) & set(nodeJ['predecessors']))
                suc = list(set(nodeI['successors']) & set(nodeJ['successors']))
                for b in list(set().union(pred, suc)):
                    w.factorize(b, i, j)
                    if wnew not in open and wnew not in close:
                        if wnew.getCost() < wmin.getCost():
                            wmin = wnew.copy()
                        open.append(wnew)

            close.append(w)
        return wmin

    def getWSign(self):
        for node in self.nodes:
            node['taskIds'] = []
        return

    def swap(self, i, j):
        if not self.isNodesAdjacent(i, j):
            print 'ERROR: Swapping of nonadjacent nodes!'
            sys.exit(0)
        if self.isNodeBranching(i):
            print 'ERROR: Swapping of branching node '+str(i)+'!'
            sys.exit(0)
        if self.isNodeBranching(j):
            print 'ERROR: Swapping of branching node '+str(j)+'!'
            sys.exit(0)
        nodeI = self.findNode(i)
        nodeJ = self.findNode(j)
        if j in nodeI['predecessors']:
            return self.swap(j, i)
        nodeI['successors'].remove(j)
        nodeI['predecessors'].append(j)
        nodeJ['predecessors'].remove(i)
        nodeJ['successors'].append(i)
        for edge in self.edges:
            if edge['targetId'] == i:
                edge['targetId'] = j
                nodeI['predecessors'].remove(edge['sourceId'])
                nodeJ['predecessors'].append(edge['sourceId'])
            if edge['sourceId'] == j:
                edge['sourceId'] = i
                nodeJ['successors'].remove(edge['targetId'])
                nodeI['successors'].append(edge['targetId'])
        return self

    def distribute(self, b, i):
        if not self.isNodesAdjacent(b, i):
            print 'ERROR: Distributing of nonadjacent nodes!'
            sys.exit(0)
        # if (self.isNodeBranching(i)):
        #     print 'ERROR: Distributing of branching node '+str(i)+'!'
        #     sys.exit(0)
        if self.isNodeUnary(b):
            print 'ERROR: Distributing over unary node '+str(b)+'!'
            sys.exit(0)
        nodeB = self.findNode(b)
        if i in nodeB['predecessors'] and len(nodeB['successors']) != 2:
            print 'ERROR: Distributing supported only into two parallel branches (you have '+str(len(nodeB['successors']))+' branches)!'
            sys.exit(0)
        if i in nodeB['successors'] and len(nodeB['predecessors']) != 2:
            print 'ERROR: Distributing supported only into two parallel branches (you have '+str(len(nodeB['predecessors']))+' branches)!'
            sys.exit(0)

        id = str(i)
        i = id+'.1'
        j = id+'.2'
        self.nodes.append({
            'name': self.findNode(i)['name'],
            'id': j,
            'taskIds': []
        })
        self.changeNodeId(id, i)
        nodeI = self.findNode(i)
        nodeJ = self.findNode(j)
        for ti in nodeI['taskIds']:
            task = self.findTask(ti)
            cTask = copy.deepcopy(task)
            cTask['nodeId'] = j
            cTask['id'] = str(cTask['id'])+'.2'
            self.tasks.append(cTask)
            nodeJ['taskIds'].append(cTask['id'])
        branches = []
        if i in nodeB['predecessors']:
            for eid, edge in self.edges:
                if edge['sourceId'] == i and edge['targetId'] == b:
                    self.edges.pop(eid)
                    nodeI['successors'].remove(b)
                    nodeB['predecessors'].remove(i)
                elif edge['targetId'] == i:
                    edge['targetId'] = b
                    nodeI['predecessors'].remove(edge['sourceId'])
                    nodeB['predecessors'].append(edge['sourceId'])
                elif edge['sourceId'] == b:
                    branches.append(edge['id'])
            if len(branches) != 2:
                print 'ERROR: Distributing supported only into two parallel branches (you have '+str(len(branches))+' branches)!'
                sys.exit(0)
            for k in range(2):
                edge = self.findEdge(branches[k])
                id = [i, j][k]
                self.edges.append({
                    'id': str(edge['id'])+'.'+str(k+1),
                    'sourceId': id,
                    'targetId': edge['targetId']
                })
                edge['targetId'] = id
                self.findNode(id)['predecessors'].append(edge['sourceId'])
        elif i in nodeB['successors']:
            for eid, edge in self.edges:
                if edge['sourceId'] == b and edge['targetId'] == i:
                    self.edges.pop(eid)
                    nodeB['successors'].remove(i)
                    nodeI['predecessors'].remove(b)
                elif edge['sourceId'] == i:
                    edge['sourceId'] = b
                    nodeI['successors'].remove(edge['targetId'])
                    nodeB['successors'].append(edge['targetId'])
                elif edge['targetId'] == b:
                    branches.append(edge['id'])
            if len(branches) != 2:
                print 'ERROR: Distributing supported only into two parallel branches (you have '+str(len(branches))+' branches)!'
                sys.exit(0)
            for k in range(2):
                edge = self.findEdge(branches[k])
                id = [i, j][k]
                self.edges.append({
                    'id': str(edge['id'])+'.'+str(k+1),
                    'sourceId': edge['sourceId'],
                    'targetId': id
                })
                edge['sourceId'] = id
                self.findNode(id)['successors'].append(edge['targetId'])
        else:
            print 'ERROR: Unexpected conditions!'
            sys.exit(0)
        return self

    def factorize(self, b, i, j):
        if not self.isNodesAdjacent(b, i) or not self.isNodesAdjacent(b, j):
            print 'ERROR: Factorizing of nonadjacent nodes!'
            sys.exit(0)
        if not self.isNodesHomologous(i, j):
            print 'ERROR: Factorizing of non homologous nodes!'
            sys.exit(0)
        if self.isNodeUnary(b):
            print 'ERROR: Factorizing over unary node '+str(b)+'!'
            sys.exit(0)
        if i.endswith(('.1', '.2')) and j.endswith(('.1', '.2')):
            id = i[:-2]
        else:
            id = str(i)+'+'+str(j)
        nodeB = self.findNode(b)
        self.findNode(i)['id'] = id
        nodeId = self.findNode(id)

        for tid, task in self.tasks:
            if task['nodeId'] == j:
                self.tasks.pop(tid)
            if task['nodeId'] == i:
                task['nodeId'] = id
        for nid, node in self.nodes:
            if node['id'] == j:
                self.nodes.pop(nid)
                break
        ei = 0
        if i in nodeB['successors'] and j in nodeB['successors']:
            if len(nodeB['predecessors']) != 1:
                print 'ERROR: Unexpected conditions!'
                sys.exit(0)
            for eid, edge in self.edges:
                if str(edge['id']) >= str(ei):
                    ei = edge['id']+str(1)
                if edge['sourceId'] == b and edge['targetId'] == i:
                    self.edges.pop(eid)
                    nodeB['successors'].remove(i)
                    nodeId['predecessors'].remove(b)
                elif edge['sourceId'] == b and edge['targetId'] == j:
                    self.edges.pop(eid)
                    nodeB['successors'].remove(j)
                elif edge['sourceId'] == i:
                    edge['sourceId'] = b
                    nodeB['successors'].append(edge['targetId'])
                    nodeId['successors'].remove(edge['targetId'])
                elif edge['sourceId'] == j:
                    edge['sourceId'] = b
                    nodeB['successors'].append(edge['targetId'])
                elif edge['targetId'] == b:
                    edge['targetId'] = id
                    nodeB['predecessors'].remove(edge['sourceId'])
                    nodeId['predecessors'].append(edge['sourceId'])
            self.edges.append({
                'id': ei,
                'sourceId': id,
                'targetId': b
            })
            nodeB['predecessors'].append(id)
            nodeId['successors'].append(b)
        elif i in nodeB['predecessors'] and j in nodeB['predecessors']:
            if len(nodeB['successors']) != 1:
                print 'ERROR: Unexpected conditions!'
                sys.exit(0)
            for eid, edge in self.edges:
                if str(edge['id']) >= str(ei):
                    ei = edge['id']+str(1)
                if edge['sourceId'] == i and edge['targetId'] == b:
                    self.edges.pop(eid)
                    nodeId['successors'].remove(b)
                    nodeB['predecessors'].remove(i)
                elif edge['sourceId'] == j and edge['targetId'] == b:
                    self.edges.pop(eid)
                    nodeB['predecessors'].remove(j)
                elif edge['targetId'] == i:
                    edge['targetId'] = b
                    nodeB['predecessors'].append(edge['targetId'])
                    nodeId['predecessors'].remove(edge['targetId'])
                elif edge['targetId'] == j:
                    edge['targetId'] = b
                    nodeB['predecessors'].append(edge['targetId'])
                elif edge['sourceId'] == b:
                    edge['sourceId'] = id
                    nodeB['successors'].remove(edge['sourceId'])
                    nodeId['successors'].append(edge['sourceId'])
            self.edges.append({
                'id': ei,
                'sourceId': b,
                'targetId': id
            })
            nodeB['successors'].append(id)
            nodeId['predecessors'].append(b)
        else:
            print 'ERROR: Unexpected conditions!'
            sys.exit(0)

        return self

    def compose(self, i, j):
        if not self.isNodesAdjacent(i, j):
            print 'ERROR: Composing of nonadjacent nodes!'
            sys.exit(0)
        if self.isNodeBranching(i):
            print 'ERROR: Composing of branching node '+str(i)+'!'
            sys.exit(0)
        if self.isNodeBranching(j):
            print 'ERROR: Composing of branching node '+str(j)+'!'
            sys.exit(0)
        nodeI = self.findNode(i)
        nodeJ = self.findNode(j)
        if j in nodeI['predecessors']:
            return self.compose(j, i)
        nodeI['taskIds'].extend(nodeJ['taskIds'])
        id = str(nodeI['id'])+'+'+str(nodeJ['id'])
        nodeI['id'] = id
        for tid in nodeI['taskIds']:
            self.findTask(tid)['nodeId'] = id
        for eid, edge in self.edges:
            if edge['sourceId'] == i and edge['targetId'] == j:
                self.edges.pop(eid)
                nodeI['successors'].remove(j)
                nodeJ['predecessors'].remove(i)
            elif edge['targetId'] == i:
                edge['targetId'] = id
                self.findNode(edge['sourceId'])['successors'].remove(i).append(id)
            elif edge['sourceId'] == j:
                edge['sourceId'] = id
                self.findNode(edge['targetId'])['predecessors'].remove(j).append(id)
            elif edge['sourceId'] == i:
                edge['sourceId'] = id
                self.findNode(edge['targetId'])['predecessors'].remove(i).append(id)
            elif edge['targetId'] == j:
                edge['targetId'] = id
                self.findNode(edge['sourceId'])['successors'].remove(j).append(id)
        for nid, node in self.nodes:
            if node['id'] == j:
                self.nodes.pop(nid)
                break
        return self

    def decompose(self, i):
        if self.isNodeBranching(i):
            print 'ERROR: Decomposing of branching node '+str(i)+'!'
            sys.exit(0)
        if '+' not in str(i):
            print 'ERROR: Decomposing supported only for previously composed of factorized nodes!'
            sys.exit(0)
        id = str(i)
        i = id.split('+')[0]
        j = id[(len(i)+1):]
        nodeI = self.findNode(id)
        nodeI['id'] = i
        taskIds = copy.deepcopy(nodeI['taskIds'])
        nodeI['taskIds'] =taskIds[0:len(taskIds)/2]
        for ti in nodeI['taskIds']:
            self.findTask(ti)['nodeId'] = i
        nodeI['successors'] = [j]
        cNode = copy.deepcopy(nodeI)
        cNode['id'] = j
        cNode['taskIds'] =taskIds[len(taskIds)/2:]
        for ti in cNode['taskIds']:
            self.findTask(ti)['nodeId'] = j
        cNode['predecessors'] = [i]
        self.nodes.append(cNode)
        nodeJ = self.findNode(j)
        eid = 0
        for edge in self.edges:
            if str(edge['id']) >= str(eid):
                eid = edge['id']+str(1)
            if edge['sourceId'] == id:
                edge['sourceId'] = i
            elif edge['targetId'] == id:
                edge['targetId'] = j
        self.edges.append({
            'id': eid,
            'sourceId': i,
            'targetId': j
        })
        return self

    def indeg(self, i):
        node = self.findNode(i)
        return len(node['predecessors'])

    def outdeg(self, i):
        node = self.findNode(i)
        return len(node['successors'])

    def isNodeUnary(self, i):
        return self.indeg(i) <= 1 and self.outdeg(i) <= 1

    def isNodeBranching(self, i):
        return not self.isNodeUnary(i)

    def isNodesAdjacent(self, i, j):
        nodeI = self.findNode(i)
        return j in nodeI['successors'] or j in nodeI['predecessors']

    def isNodesHomologous(self, i, j):
        nodeI = self.findNode(i)
        nodeJ = self.findNode(j)
        if len(nodeI['taskIds']) != len(nodeJ['taskIds']):
            return False
        else:
            nt = len(nodeI['taskIds'])
        for k in range(0, nt):
            p = nodeI['taskIds'][k]
            q = nodeJ['taskIds'][k]
            if cmp(self.findTask(p)['operator'], self.findTask(q)['operator']) != 0:
                return False
        return True

    def findHomologousNodes(self):
        HP = []
        for nodeI in self.nodes:
            for nodeJ in self.nodes:
                i = nodeI['id']
                j = nodeJ['id']
                if i <= j:
                    continue
                if self.isNodesHomologous(i, j):
                    HP.append((i, j))
        return HP

    def findLinearPaths(self):
        LP = []
        for edge in self.edges:
            i = edge['sourceId']
            j = edge['targetId']
            if self.isNodeUnary(i) and self.isNodeUnary(j):
                LP.append(edge['id'])
        return LP

    def findNode(self, id):
        for node in self.nodes:
            if str(id) == str(node['id']):
                return node
        print 'ERROR: Node with id '+str(id)+' not found!'
        sys.exit(0)

    def findTask(self, id):
        for task in self.tasks:
            if str(id) == str(task['id']):
                return task
        print 'ERROR: Task with id '+str(id)+' not found!'
        sys.exit(0)

    def findEdge(self, id):
        for edge in self.edges:
            if str(id) == str(edge['id']):
                return edge
        print 'ERROR: Edge with id '+str(id)+' not found!'
        sys.exit(0)

    def changeNodeId(self, old, new):
        self.findNode(old)['id'] = new
        for edge in self.edges:
            if edge['sourceId'] == old:
                edge['sourceId'] = new
                self.findNode(edge['targetId'])['predecessors'].remove(old).append(new)
            if edge['targetId'] == old:
                edge['targetId'] = new
                self.findNode(edge['sourceId'])['successors'].remove(old).append(new)
        for task in self.tasks:
            if task['nodeId'] == old:
                task['nodeId'] = new

    def getCost(self):
        # TODO: getCost from IReS
        return len(self.nodes)

    def execute(self):
        current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%s")
        fname = self.name + '_' + current_time
        if not os.path.exists(self.WLibrary+fname):
            os.makedirs(self.WLibrary+fname)
        else:
            print 'ERROR: Folder '+fname+' is exist!'
            sys.exit(0)
        os.makedirs(self.WLibrary+fname+'/'+'operators')
        os.makedirs(self.WLibrary+fname+'/'+'datasets')
        graph = ''
        targ = ''
        dn = 1
        for edge in self.edges:
            inp = edge['sourceId']
            out = edge['targetId']
            nodeI = self.findNode(inp)
            nodeO = self.findNode(out)
            taskIid = nodeI['taskIds'][0]
            taskOid = nodeO['taskIds'][0]
            taskI = self.findTask(taskIid)
            taskO = self.findTask(taskOid)

            if len(self.findNode(out)['successors']) == 0:
                targ = taskO['name']

            for task in [taskI, taskO]:
                if 'type' in task and task['type'] == 'dataset':
                    dir = 'datasets'
                else:
                    dir = 'operators'
                if not os.path.isfile(dir + '/' + task['name']):
                    constr = ''
                    for d in dict2text(task['operator']):
                        constr = constr + d + '\n'
                    file = open(os.path.join(self.WLibrary, fname, dir, task['name']), 'wb')
                    file.write(constr)
                    file.close()
            if 'type' in taskI and taskI['type'] == 'dataset':
                if len(nodeO['predecessors']) == 1:
                    graph = graph + taskI['name'] + ',' + taskO['name'] + '\n'
                else:
                    graph = graph + taskI['name'] + ',' + taskO['name'] + ',' + str(nodeO['predecessors'].index(inp)) + '\n'
            elif 'type' in taskO and taskO['type'] == 'dataset':
                if len(nodeI['successors']) == 1:
                    graph = graph + taskI['name'] + ',' + taskO['name'] + '\n'
                else:
                    graph = graph + taskI['name'] + ',' + taskO['name'] + str(nodeI['successors'].index(out)) + '\n'
            else:
                if len(nodeI['successors']) == 1:
                    graph = graph + taskI['name'] + ',d' + str(dn) + '\n'
                else:
                    graph = graph + taskI['name'] + ',d' + str(dn) + ',' + str(nodeI['successors'].index(out)) + '\n'
                if len(nodeO['predecessors']) == 1:
                    graph = graph + 'd' + str(dn) + ',' + taskO['name'] + '\n'
                else:
                    graph = graph + 'd' + str(dn) + ',' + taskO['name'] + ',' + str(nodeO['predecessors'].index(inp)) + '\n'
                file = open(os.path.join(self.WLibrary, fname, 'datasets', 'd'+str(dn)), 'wb')
                file.write('')
                file.close()
                dn = dn+1

        graph = graph + targ + ',$$target\n'
        file = open(os.path.join(self.WLibrary, fname, 'graph'), 'wb')
        file.write(graph)
        file.close()

        py_dir = os.path.dirname(os.path.realpath(__file__))
        os.chdir(py_dir)
        os.system('java -cp ~/asap/IRES-Platform/asap-platform/asap-client/target/ASAP_client.jar gr.ntua.cslab.asap.examples.AddWorkflowFromDir localhost '+self.name+' '+fname)

    def save(self, add=None):
        current_time = datetime.now().strftime("%Y-%m-%d_%H:%M")
        fname = self.name + '_' + current_time
        fname = fname+add if add else fname
        if not os.path.exists(self.WLibrary):
            os.makedirs(self.WLibrary)
        file = open(os.path.join(self.WLibrary, fname), 'w')
        wl = {
            'name': self.name,
            'nodes': self.nodes,
            'edges': self.edges,
            'tasks': self.tasks,
            'taskLinks': self.taskLinks
        }
        file.write(json.dumps(wl))
        file.close()
        return os.path.join(self.WLibrary, fname)


def dict2text(indict, pre=None):
    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                for d in dict2text(value, pre+'.'+key if pre else key):
                    yield d
            elif isinstance(value, list) or isinstance(value, tuple):
                for v in value:
                    for d in dict2text(v, pre+'.'+key if pre else key):
                        yield d
            else:
                yield pre+'.'+key+'='+str(value) if pre else key+'='+str(value)
    else:
        yield indict

if __name__ == "__main__":
    if len(sys.argv) == 3:
        action = sys.argv[1]
        fname = sys.argv[2]
    else:
        print 'ERROR: Wrong number of arguments!'
        sys.exit(0)

    w = Workflow(fname)

    if action == 'analyse':
        w.analyse()
        print w.save('-analysed')
    elif action == 'optimise':
        w.analyse()
        w.optimise()
        # w.hs()
        # w.es()
        print w.save('-optimised')
    elif action == 'execute':
        w.analyse()
        w.execute()
    else:
        print 'ERROR: Unsupported action '+sys.argv[1]+'!'
        sys.exit(0)

