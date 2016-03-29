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
            sys.exit('ERROR: File %s was not found!' % fname)
        fl = open(fname, 'r')
        wl = yaml.safe_load(fl)
        fl.close()
        self.name = wl['name'] if 'name' in wl else 'workflow'
        self.nodes = wl['nodes'] if 'nodes' in wl else []
        self.edges = wl['edges'] if 'edges' in wl else []
        self.tasks = wl['tasks'] if 'tasks' in wl else []
        self.taskLinks = wl['taskLinks'] if 'taskLinks' in wl else []

    def __repr__(self):
        return {
            'name': self.name,
            'nodes': self.nodes,
            'edges': self.edges,
            'tasks': self.tasks,
            'taskLinks': self.taskLinks
        }

    def analyse(self):
        for node in self.nodes:
            node['predecessors'] = []
            node['successors'] = []
            node['taskIds'] = []
        for task in self.tasks:
            nid = task['nodeId']
            self.findNode(nid)['taskIds'].append(task['id'])
        for edge in self.edges:
            inp = edge['sourceId']
            out = edge['targetId']
            self.findNode(inp)['successors'].append(out)
            self.findNode(out)['predecessors'].append(inp)
            edge['analysis'] = {}
            for task in self.tasks:
                inpdict = {}
                outdict = {}
                edge['analysis']['data_info'] = {}
                if (task['nodeId'] == inp):
                    if ('json' in task.keys()):
                        inpdict = copy.deepcopy(task['json'].values()[0].values()[0])
                        # if ('data' in task['json'].keys()):
                        #     inpdict = task['json'].values()[0].values()[0]
                        # else:
                        #     inpdict = task['json'].values()[0].values()[0]['output']
                        # edge['analysis']['data_info'] = inpdict['data_info'].copy()
                        edge['analysis']['data_info'].update(inpdict)
                if (task['nodeId'] == out):
                    if ('json' in task.keys()):
                        outdict = task['json'].values()[0].values()[0]
                        # if ('data' in task['json'].keys()):
                        #     outdict = task['json'].values()[0].values()[0]
                        # else:
                        #     outdict = task['json'].values()[0].values()[0]['input']
                        # edge['analysis']['data_info'].update(outdict['data_info'])
                        edge['analysis']['data_info'].update(outdict)
                if ('engine' in inpdict.keys() and 'engine' in outdict.keys()):
                    if (inpdict['engine']['DB'] == outdict['engine']['DB']):
                        edge['analysis']['engine'] = copy.deepcopy(inpdict['engine'])
                    else:
                        edge['analysis']['engine'] = {}
                        edge['analysis']['engine']['from'] = copy.deepcopy(inpdict['engine'])
                        edge['analysis']['engine']['to'] = copy.deepcopy(outdict['engine'])
                        edge['analysis']['message'].append('formats convertation')
                elif ('engine' in inpdict.keys()):
                    edge['analysis']['engine'] = copy.deepcopy(inpdict['engine'])
                elif ('engine' in outdict.keys()):
                    edge['analysis']['engine'] = copy.deepcopy(outdict['engine'])
            # print edge['analysis']

    def optimise(self):
        moved = -1
        while (moved != 0):
            moved = 0
            for edge in self.edges:
                i = edge['sourceId']
                j = edge['targetId']
                ni = self.findNode(i)
                nj = self.findNode(j)
                if (self.isNodeUnary(i) and self.isNodeUnary(j) and len(ni['taskIds']) == 1 and len(nj['taskIds']) == 1):
                    ti = self.findTask(ni['taskIds'][0])
                    tj = self.findTask(nj['taskIds'][0])
                    if ('operator' in ti and 'constraints' in ti['operator'] or 'name' in ti['operator']['constraints'] and 'filter' in ti['operator']['constraints']['name'] and 'select' in ti['operator']['constraints']['name']):
                        continue
                    # heuristic 1
                    # move restrictive operators to the start
                    elif ('operator' in tj and 'constraints' in tj['operator'] or 'name' in tj['operator']['constraints'] and 'filter' in tj['operator']['constraints']['name'] and 'select' in tj['operator']['constraints']['name']):
                        ni['taskIds'][0] = tj['id']
                        ti['nodeId'] = int(nj['id'])
                        nj['taskIds'][0] = ti['id']
                        tj['nodeId'] = int(ni['id'])
                        moved = moved + 1
                        # print ti
                        # print tj
                    elif ('operator' in ti and 'constraints' in ti['operator'] or 'name' in ti['operator']['constraints'] and 'calc' in ti['operator']['constraints']['name']):
                        continue
                    # heuristic 2
                    # place non-blocking operators together and separately from blocking operators
                    elif ('operator' in tj and 'constraints' in tj['operator'] or 'name' in tj['operator']['constraints'] and 'calc' in tj['operator']['constraints']['name']):
                        ni['taskIds'][0] = tj['id']
                        ti['nodeId'] = int(nj['id'])
                        nj['taskIds'][0] = ti['id']
                        tj['nodeId'] = int(ni['id'])
                        moved = moved + 1
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

        while len(open) <> 0:
            w = open.pop()
            # composing all possible pairs
            for edge in self.edges:
                inp = edge['sourceId']
                out = edge['targetId']
                wnew = w.compose(inp, out)
                if (wnew not in open and wnew not in close):
                    if wnew.getCost() < wmin.getCost():
                        wmin = wnew.copy()
                    open.append(wnew)

            # swapping all possible pairs
            for edge in self.edges:
                inp = edge['sourceId']
                out = edge['targetId']
                w.swap(inp, out)
                if (wnew not in open and wnew not in close):
                    if wnew.getCost() < wmin.getCost():
                        wmin = wnew.copy()
                    open.append(wnew)

            # factorizing all pairs of homologous nodes
            for pair in HP:
                inp = pair.first
                out = pair.second
                w.factorize(inp, out)
                if (wnew not in open and wnew not in close):
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

        while len(open) <> 0:
            w = open.pop()
            # composing all possible pairs
            for k in LP:
                edge = self.edges[k]
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
                if (wnew not in open and wnew not in close):
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
                    if (wnew not in open and wnew not in close):
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
        if (not self.isNodesAdjacent(i, j)):
            sys.exit('ERROR: Swapping of nonadjacent nodes!')
        if (self.isNodeBranching(i)):
            sys.exit('ERROR: Swapping of branching node %s!' % i)
        if (self.isNodeBranching(j)):
            sys.exit('ERROR: Swapping of branching node %s!' % j)
        nodeI = self.findNode[i]
        nodeJ = self.findNode[j]
        if (j in nodeI['predecessors']):
            return self.swap(j, i)
        nodeI['successors'].remove(j)
        nodeI['predecessors'].append(j)
        nodeJ['predecessors'].remove(i)
        nodeJ['successors'].append(i)
        for edge in self.edges:
            if (edge['targetId'] == i):
                edge['targetId'] = j
                nodeI['predecessors'].remove(edge['sourceId'])
                nodeJ['predecessors'].append(edge['sourceId'])
            if (edge['sourceId'] == j):
                edge['sourceId'] = i
                nodeJ['successors'].remove(edge['targetId'])
                nodeI['successors'].append(edge['targetId'])
        return self

    def distribute(self, b, i):
        if (not self.isNodesAdjacent(b, i)):
            sys.exit('ERROR: Distributing of nonadjacent nodes!')
        # if (self.isNodeBranching(i)):
        #     sys.exit('ERROR: Distributing of branching node %s!' % i)
        if (self.isNodeUnary(b)):
            sys.exit('ERROR: Distributing over unary node %s!' % b)
        nodeB = self.findNode(b)
        if (i in nodeB['predecessors'] and len(nodeB['successors']) <> 2):
            sys.exit('ERROR: Distributing supported only into two parallel branches (you have %s branches)!' % len(nodeB['successors']))
        if (i in nodeB['successors'] and len(nodeB['predecessors']) <> 2):
            sys.exit('ERROR: Distributing supported only into two parallel branches (you have %s branches)!' % len(nodeB['predecessors']))

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
        if (i in nodeB['predecessors']):
            for eid, edge in self.edges:
                if (edge['sourceId'] == i and edge['targetId'] == b):
                    self.edges.pop(eid)
                    nodeI['successors'].remove(b)
                    nodeB['predecessors'].remove(i)
                elif (edge['targetId'] == i):
                    edge['targetId'] = b
                    nodeI['predecessors'].remove(edge['sourceId'])
                    nodeB['predecessors'].append(edge['sourceId'])
                elif (edge['sourceId'] == b):
                    branches.append(edge['id'])
            if (len(branches) <> 2):
                sys.exit('ERROR: Distributing supported only into two parallel branches (you have %s branches)!' % len(branches))
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
        elif (i in nodeB['successors']):
            for eid, edge in self.edges:
                if (edge['sourceId'] == b and edge['targetId'] == i):
                    self.edges.pop(eid)
                    nodeB['successors'].remove(i)
                    nodeI['predecessors'].remove(b)
                elif (edge['sourceId'] == i):
                    edge['sourceId'] = b
                    nodeI['successors'].remove(edge['targetId'])
                    nodeB['successors'].append(edge['targetId'])
                elif (edge['targetId'] == b):
                    branches.append(edge['id'])
            if (len(branches) <> 2):
                sys.exit('ERROR: Distributing supported only into two parallel branches (you have %s branches)!' % len(branches))
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
            sys.exit('ERROR: Unexpected conditions!')
        return self

    def factorize(self, b, i, j):
        if (not self.isNodesAdjacent(b, i) or not self.isNodesAdjacent(b, j)):
            sys.exit('ERROR: Factorizing of nonadjacent nodes!')
        if (not self.isNodesHomologous(i, j)):
            sys.exit('ERROR: Factorizing of non homologous nodes!')
        if (self.isNodeUnary(b)):
            sys.exit('ERROR: Factorizing over unary node %s!' % b)
        if (i.endswith(('.1', '.2')) and j.endswith(('.1', '.2'))):
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
        if (i in nodeB['successors'] and j in nodeB['successors']):
            if (len(nodeB['predecessors']) <> 1):
                sys.exit('ERROR: Unexpected conditions!')
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
        elif (i in nodeB['predecessors'] and j in nodeB['predecessors']):
            if (len(nodeB['successors']) <> 1):
                sys.exit('ERROR: Unexpected conditions!')
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
            sys.exit('ERROR: Unexpected conditions!')

        return self

    def compose(self, i, j):
        if (not self.isNodesAdjacent(i, j)):
            sys.exit('ERROR: Composing of nonadjacent nodes!')
        if (self.isNodeBranching(i)):
            sys.exit('ERROR: Composing of branching node %s!' % i)
        if (self.isNodeBranching(j)):
            sys.exit('ERROR: Composing of branching node %s!' % j)
        nodeI = self.findNode(i)
        nodeJ = self.findNode(j)
        if (j in nodeI['predecessors']):
            return self.compose(j, i)
        nodeI['taskIds'].extend(nodeJ['taskIds'])
        id = str(nodeI['id'])+'+'+str(nodeJ['id'])
        nodeI['id'] = id
        for tid in nodeI['taskIds']:
            self.findTask(tid)['nodeId'] = id
        for eid, edge in self.edges:
            if (edge['sourceId'] == i and edge['targetId'] == j):
                self.edges.pop(eid)
                nodeI['successors'].remove(j)
                nodeJ['predecessors'].remove(i)
            elif (edge['targetId'] == i):
                edge['targetId'] = id
                self.findNode(edge['sourceId'])['successors'].remove(i).append(id)
            elif (edge['sourceId'] == j):
                edge['sourceId'] = id
                self.findNode(edge['targetId'])['predecessors'].remove(j).append(id)
            elif (edge['sourceId'] == i):
                edge['sourceId'] = id
                self.findNode(edge['targetId'])['predecessors'].remove(i).append(id)
            elif (edge['targetId'] == j):
                edge['targetId'] = id
                self.findNode(edge['sourceId'])['successors'].remove(j).append(id)
        for nid, node in self.nodes:
            if node['id'] == j:
                self.nodes.pop(nid)
                break
        return self

    def decompose(self, i):
        if (self.isNodeBranching(i)):
            sys.exit('ERROR: Decomposing of branching node %s!' % i)
        if ('+' not in str(i)):
            sys.exit('ERROR: Decomposing supported only for previously composed of factorized nodes!')
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
        return (self.indeg(i) <= 1 and self.outdeg(i) <= 1)

    def isNodeBranching(self, i):
        return not self.isNodeUnary(i)

    def isNodesAdjacent(self, i, j):
        nodeI = self.findNode(i)
        return (j in nodeI['successors'] or j in nodeI['predecessors'])

    def isNodesHomologous(self, i, j):
        nodeI = self.findNode(i)
        nodeJ = self.findNode(j)
        if len(nodeI['taskIds']) <> len(nodeJ['taskIds']):
            return False
        else:
            nt = len(nodeI['taskIds'])
        for k in range(0, nt):
            p = nodeI['taskIds'][k]
            q = nodeJ['taskIds'][k]
            if (cmp(self.findTask(p)['operator'], self.findTask(q)['operator']) <> 0):
                return False
        return True

    def findHomologousNodes(self):
        HP = []
        for nodeI in self.nodes:
            for nodeJ in self.nodes:
                i = nodeI['id']
                j = nodeJ['id']
                if (i <= j):
                    continue
                if self.isNodesHomologous(i, j):
                    HP.append((i, j))
        return HP

    def findLinearPaths(self):
        LP = []
        for edge in self.edges:
            i = edge['sourceId']
            j = edge['targetId']
            if (self.isNodeUnary(i) and self.isNodeUnary(j)):
                LP.append(edge['id'])
        return LP

    def findNode(self, id):
        for node in self.nodes:
            if str(id) == str(node['id']):
                return node
        sys.exit('ERROR: Node with id %s not found!' % id)

    def findTask(self, id):
        for task in self.tasks:
            if str(id) == str(task['id']):
                return task
        sys.exit('ERROR: Task with id %s not found!' % id)

    def findEdge(self, id):
        for edge in self.edges:
            if str(id) == str(edge['id']):
                return edge
        sys.exit('ERROR: Edge with id %s not found!' % id)

    def changeNodeId(self, old, new):
        self.findNode(old)['id'] = new
        for edge in self.edges:
            if (edge['sourceId'] == old):
                edge['sourceId'] = new
                self.findNode(edge['targetId'])['predecessors'].remove(old).append(new)
            if (edge['targetId'] == old):
                edge['targetId'] = new
                self.findNode(edge['sourceId'])['successors'].remove(old).append(new)
        for task in self.tasks:
            if (task['nodeId'] == old):
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
            sys.exit('ERROR: Folder %s is exist!' % fname)
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
                if ('type' in task and task['type'] == 'dataset'):
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
            if ('type' in taskI and taskI['type'] == 'dataset'):
                if len(nodeO['predecessors']) == 1:
                    graph = graph + taskI['name'] + ',' + taskO['name'] + '\n'
                else:
                    graph = graph + taskI['name'] + ',' + taskO['name'] + ',' + str(nodeO['predecessors'].index(inp)) + '\n'
            elif ('type' in taskO and taskO['type'] == 'dataset'):
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
                dn = dn+1

        graph = graph + targ + ',$$target\n'
        file = open(os.path.join(self.WLibrary, fname, 'graph'), 'wb')
        file.write(graph)
        file.close()

        py_dir = os.path.dirname(os.path.realpath(__file__))
        os.chdir(py_dir)
        os.system('java -cp ASAP_client.jar ExecuteWorkflow '+self.name+' '+fname)

    def save(self, add = None):
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

def dict2text(indict, pre = None):
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
        sys.exit('ERROR: Wrong number of arguments!')

    w = Workflow(fname)

    if (action == 'analyse'):
        w.analyse()
        print w.save('-analysed')
    elif (action == 'optimise'):
        w.analyse()
        w.optimise()
        # w.hs()
        # w.es()
        print w.save('-optimised')
    elif (action == 'execute'):
        w.analyse()
        w.execute()
    else:
        sys.exit('ERROR: Unsupported action %s!' % sys.argv[1])

