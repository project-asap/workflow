#!/usr/bin/env python
import sys, os
import json
import ruamel.yaml as yaml
import copy

def analyse(wl):
    for node in wl['nodes']:
        node['n_in'] = 0
        node['n_out'] = 0
        node['tasks'] = []
    for task in wl['tasks']:
        nid = task['nodeId']
        wl['nodes'][int(nid)]['tasks'].append(task['id'])
    for link in wl['links']:
        inp = link['sourceId']
        out = link['targetId']
        wl['nodes'][int(inp)]['n_out'] = wl['nodes'][int(inp)]['n_out']+1
        wl['nodes'][int(out)]['n_in'] = wl['nodes'][int(out)]['n_in']+1
        link['analysis'] = {}
        for task in wl['tasks']:
            inpdict = {}
            outdict = {}
            link['analysis']['data_info'] = {}
            if (task['nodeId'] == inp):
                if ('json' in task.keys()):
                    inpdict = copy.deepcopy(task['json'].values()[0].values()[0])
                    # if ('data' in task['json'].keys()):
                    #     inpdict = task['json'].values()[0].values()[0]
                    # else:
                    #     inpdict = task['json'].values()[0].values()[0]['output']
                    # link['analysis']['data_info'] = inpdict['data_info'].copy()
                    link['analysis']['data_info'].update(inpdict)
            if (task['nodeId'] == out):
                if ('json' in task.keys()):
                    outdict = task['json'].values()[0].values()[0]
                    # if ('data' in task['json'].keys()):
                    #     outdict = task['json'].values()[0].values()[0]
                    # else:
                    #     outdict = task['json'].values()[0].values()[0]['input']
                    # link['analysis']['data_info'].update(outdict['data_info'])
                    link['analysis']['data_info'].update(outdict)
            if ('engine' in inpdict.keys() and 'engine' in outdict.keys()):
                if (inpdict['engine']['DB'] == outdict['engine']['DB']):
                    link['analysis']['engine'] = copy.deepcopy(inpdict['engine'])
                else:
                    link['analysis']['engine'] = {}
                    link['analysis']['engine']['from'] = copy.deepcopy(inpdict['engine'])
                    link['analysis']['engine']['to'] = copy.deepcopy(outdict['engine'])
                    link['analysis']['message'].append('formats convertation')
            elif ('engine' in inpdict.keys()):
                link['analysis']['engine'] = copy.deepcopy(inpdict['engine'])
            elif ('engine' in outdict.keys()):
                link['analysis']['engine'] = copy.deepcopy(outdict['engine'])
        print link['analysis']
    return wl

def optimise(wl):
    moved = -1
    while (moved != 0):
        moved = 0
        for link in wl['links']:
            inp = link['sourceId']
            out = link['targetId']
            ninp = wl['nodes'][int(inp)]
            nout = wl['nodes'][int(out)]
            if (ninp['n_in'] == 1 and ninp['n_out'] == 1 and len(ninp['tasks']) and nout['n_in'] == 1 and nout['n_out'] == 1 and len(nout['tasks'])):
                tinp = wl['tasks'][int(ninp['tasks'][0])]
                tout = wl['tasks'][int(nout['tasks'][0])]
                if ('json' in tinp and ('select' in tinp['json'] or 'filter' in tinp['json'])):
                    continue
                # heuristic 1
                # move restrictive operators to the start
                elif ('json' in tout and ('select' in tout['json'] or 'filter' in tout['json'])):
                    ninp['tasks'][0] = tout['id']
                    tinp['nodeId'] = int(nout['id'])
                    nout['tasks'][0] = tinp['id']
                    tout['nodeId'] = int(ninp['id'])
                    moved = moved + 1
                    print tinp
                    print tout
                elif ('json' in tinp and 'calc' in tinp['json']):
                    continue
                # heuristic 2
                # place non-blocking operators together and separately from blocking operators
                elif ('json' in tout and 'calc' in tout['json']):
                    ninp['tasks'][0] = tout['id']
                    tinp['nodeId'] = int(nout['id'])
                    nout['tasks'][0] = tinp['id']
                    tout['nodeId'] = int(ninp['id'])
                    moved = moved + 1
                    print tinp
                    print tout
                else:
                    continue
            else:
                continue
        print moved
    return wl

def main(argv):
    fl = open('workflow', 'r')
    wl = yaml.safe_load(fl)
    fl.close()
    if ('analyse' in argv):
        wl = analyse(wl)
    elif ('optimise' in argv):
        wl = analyse(wl)
        wl = optimise(wl)
        wl = analyse(wl)
    fl_res = open('workflow_res', 'w')
    fl_res.seek(0)
    fl_res.write(json.dumps(wl))
    fl_res.close()


if __name__ == "__main__":
    main(sys.argv[1:])