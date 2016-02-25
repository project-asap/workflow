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
            nid = int(task['nodeId'])
            self.nodes[nid]['taskIds'].append(int(task['id']))
        for edge in self.edges:
            inp = int(edge['sourceId'])
            out = int(edge['targetId'])
            self.nodes[inp]['successors'].append(int(self.nodes[inp]['id']))
            self.nodes[out]['predecessors'].append(int(self.nodes[out]['id']))
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
                i = int(edge['sourceId'])
                j = int(edge['targetId'])
                ni = self.nodes[i]
                nj = self.nodes[j]
                if (self.isNodeUnary(i) and self.isNodeUnary(j) and len(ni['taskIds']) == 1 and len(nj['taskIds']) == 1):
                    ti = self.tasks[int(ni['taskIds'][0])]
                    tj = self.tasks[int(nj['taskIds'][0])]
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
        return copy.copy(self)

    def es(self):
        wmin = self.copy()
        open = [self]
        close = []

        HP = self.findHomologousNodes()

        while len(open) <> 0:
            w = open.pop()
            # composing all possible pairs
            for edge in self.edges:
                inp = int(edge['sourceId'])
                out = int(edge['targetId'])
                wnew = w.compose(inp, out)
                if (wnew not in open and wnew not in close):
                    if wnew.getCost() < wmin.getCost():
                        wmin = wnew.copy()
                    open.append(wnew)

            # swapping all possible pairs
            for edge in self.edges:
                inp = int(edge['sourceId'])
                out = int(edge['targetId'])
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
                inp = int(edge['sourceId'])
                out = int(edge['targetId'])
                wnew = w.compose(inp, out)
                if (wnew not in open and wnew not in close):
                    if wnew.getCost() < wmin.getCost():
                        wmin = wnew.copy()
                    open.append(wnew)

            # swapping all possible pairs
            for k in LP:
                edge = self.edges[k]
                inp = int(edge['sourceId'])
                out = int(edge['targetId'])
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

    def getWSign(self):
        for node in self.nodes:
            node['taskIds'] = []
        return

    def swap(self, i, j):
        # if (not self.isNodesAdjacent(i, j)):
        #     sys.exit('ERROR: Swapping of nonadjacent nodes!')

        return self

    def distribute(self, b, i):
        return self

    def factorize(self, b, i, j):
        return self

    def compose(self, i, j):
        # if (not self.isNodesAdjacent(i, j)):
        #     sys.exit('ERROR: Composing of nonadjacent nodes!')
        return self

    def decompose(self, i):
        return self

    def indeg(self, i):
        return len(self.nodes[i]['predecessors'])

    def outdeg(self, i):
        return len(self.nodes[i]['successors'])

    def isNodeUnary(self, i):
        return (self.indeg(i) <= 1 and self.outdeg(i) <= 1)

    def isNodeBranching(self, i):
        return not self.isNodeUnary(i)

    def isNodesAdjacent(self, i, j):
        return (j in self.nodes[i]['successors'] or j in self.nodes[i]['predecessors'])

    def isNodesHomologous(self, i, j):
        if len(self.nodes[i]['taskIds']) <> len(self.nodes[j]['taskIds']):
            return False
        else:
            nt = len(self.nodes[i]['taskIds'])
        for k in range(0, nt):
            p = self.nodes[i]['taskIds'][k]
            q = self.nodes[j]['taskIds'][k]
            if (cmp(self.tasks[p]['operator']['constraints'], self.tasks[q]['operator']['constraints']) <> 0):
                return False
        return True

    def findHomologousNodes(self):
        HP = []
        for i, a in self.nodes:
            for j, b in self.nodes:
                if (i <= j):
                    continue
                if self.isNodesHomologous(i, j):
                    HP.append((i, j))
        return HP

    def findLinearPaths(self):
        LP = []
        for k, edge in self.edges:
            i = int(edge['sourceId'])
            j = int(edge['targetId'])
            if (self.isNodeUnary(i) and self.isNodeUnary(j)):
                LP.append(k)
        return LP

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
        for edge in self.edges:
            inp = int(edge['sourceId'])
            out = int(edge['targetId'])
            taskIid = int(self.nodes[inp]['taskIds'][0])
            taskOid = int(self.nodes[out]['taskIds'][0])
            taskI = self.tasks[taskIid]
            taskO = self.tasks[taskOid]
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
            graph = graph + taskI['name'] + ',' + taskO['name'] + '\n'

        file = open(os.path.join(self.WLibrary, fname, 'graph'), 'wb')
        file.write(graph)
        file.close()

        py_dir = os.path.dirname(os.path.realpath(__file__))
        os.chdir(py_dir)
        os.system('java -cp . ExecuteWorkflow '+self.name+' '+fname)

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
                yield pre+'.'+key+'='+value if pre else key+'='+value
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
        w.execute()
    else:
        sys.exit('ERROR: Unsupported action %s!' % sys.argv[1])

