# Copyright 2016 ASAP.
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
workflow = null

nodeSelected = null
taskSelected = null

addingLink = false
node1 = null
node2 = null
nodeLink = false
taskLink = false

ires_uri = 'http://localhost:1323'

openWorkflow = (w) ->
  workflow = w

  graph.clean()
  $('#node').addClass('hide')
  $('#taskName').addClass('hide')
  $('#metadata').addClass('hide')
  $('#libraryDatastores').addClass('hide')
  $('#libraryOperators').addClass('hide')
  $('#addlink').parent('li').removeClass('active')
  $('#addTask').parent('li').removeClass('active')
  addingLink = false

  for node in w.nodes
    graph.addNode(node)
  for edge in w.edges
    graph.addLink(edge)
  return

findTask = (taskId) ->
  for task in workflow.tasks
    if parseInt(task.id) == taskId
      return task

showTasks = (nodeId) ->
  tgraph.clean()
  for task in workflow.tasks
    if parseInt(task.nodeId) == nodeId
      tgraph.addNode(task)
  for link in workflow.taskLinks
    tgraph.addLink(link)
  return

loadFile = ->
  input = $('#uploadfile')[0]
  file = input.files[0]
  fr = new FileReader()
  fr.onload = (e) ->
    lines = e.target.result
    newWorkflow = JSON.parse(lines)
    openWorkflow(newWorkflow)
    $('#uploadfile').replaceWith( $('#uploadfile').clone(true) )
  fr.readAsText(file)

selectNode = (id, type) ->
  $('#node').removeClass('hide')
  $('#libraryDatastores').addClass('hide')
  $('#libraryOperators').addClass('hide')
  if type == 'task'
    $('#taskName').removeClass('hide')
    $('#metadata').removeClass('hide')
    if (!isNaN(parseInt(taskSelected)))
      oldclass = $('#tasksBoard').find('.node'+taskSelected).attr('class')
      if !!oldclass
        newclass = oldclass.replace('selected', '');
        $('#tasksBoard').find('.node'+taskSelected).attr('class', newclass)
    taskSelected = id
    oldclass = $('#tasksBoard').find('.node'+taskSelected).attr('class')
    $('#tasksBoard').find('.node'+taskSelected).attr('class', oldclass+' selected')
    task = findTask(id)
    $('#taskTitle').val(task.name)
    $('#metadataEditor').val(JSON.stringify(task.operator, null, 2))


#    $('#metadataTree').removeClass('hide')
#    flare = task.json
#    flare.x0 = 0
#    flare.y0 = 0
#    updateMetaTree(flare)

    if (addingLink)
      if (nodeLink || isNaN(parseInt(node1)))
        taskLink = true
        nodeLink = false
        node1 = taskSelected
        node2 = null
      if (!isNaN(parseInt(node1)) && node1 != taskSelected)
        node2 = taskSelected
        link =
          'sourceId': node1
          'targetId': node2
          'id': workflow.taskLinks.length
        tgraph.addLink(link)
        workflow.taskLinks.push link
        taskLink = false
        node1 = null
        node2 = null
  else
    $('#taskName').addClass('hide')
    $('#metadata').addClass('hide')
    if (!isNaN(parseInt(nodeSelected)))
      oldclass = $('#wlBoard').find('.node'+nodeSelected).attr('class')
      if !!oldclass
        newclass = oldclass.replace('selected', '');
        $('#wlBoard').find('.node'+nodeSelected).attr('class', newclass)
    nodeSelected = id
    oldclass = $('#wlBoard').find('.node'+nodeSelected).attr('class')
    $('#wlBoard').find('.node'+nodeSelected).attr('class', oldclass+' selected')
    for node in workflow.nodes
      if parseInt(node.id) == id
        $('#nodeTitle').val(node.name)
    showTasks(id)

    if (addingLink)
      if (taskLink || isNaN(parseInt(node1)))
        taskLink = false
        nodeLink = true
        node1 = nodeSelected
        node2 = null
      if (!isNaN(parseInt(node1)) && node1 != nodeSelected)
        node2 = nodeSelected
        link =
          'sourceId': node1
          'targetId': node2
          'id': workflow.edges.length
        graph.addLink(link)
        workflow.edges.push link
        nodeLink = false
        node1 = null
        node2 = null

get_tasks = (node) ->
    (t for t in workflow.tasks when t.nodeId == node.id)

is_operator = (node=workflow.nodes[nodeSelected]) ->
    tasks = get_tasks(node)
    if tasks.length <= 0
        if node.class? and  node.class == 'circle' then false else true
    else
        t = tasks[0]
        if 'type' of t and t.type == 'dataset' then false else true

get_field_values = (node, s='') ->
    if node.children? and node.children.length > 0
        get_field_values(n, s + node.name + '.') for n in node.children
    else
        (s + node.name + '=' + node.value).split('.')[1..].join('.')


is_empty = (o) ->
    Object.keys(o).length == 0

get_description = (node) ->
    tasks = get_tasks(node)
    if tasks.length <= 0
        ''
    else
        if is_empty(tasks[0].operator) then '' else get_field_values(tasks[0].operator).join('\n')

is_abstract = (node) ->
    if is_operator(node)
        true
    else
        tasks = get_tasks(node)
        if tasks.length <= 0
            true
        else
            if is_empty(tasks[0].operator) then true else false

new_task = ->
    nodeName = prompt('Please enter task name', '')
    update_name(nodeName)
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': nodeName
      'nodeId': nodeSelected
    if not is_operator()
        task.class = 'circle'
        task.type = 'dataset'
        task.operator = {}
    else
      task.operator =
          'constraints': {}
    tgraph.addNode(task)
    workflow.tasks.push task

update_name = (name, node=workflow.nodes[nodeSelected]) ->
    #tgraph.setNodeName(node, name)
    node.name = name
    $('#wlBoard').find('.node'+nodeSelected+' text').text(name)
    $('#nodeTitle').val(name)

$(document).ready ->
  $('#newwl').click ->
    wlName = prompt('Please enter workflow name', '')
    nw =
      'name': wlName
      'nodes': []
      'edges': []
      'tasks': []
      'taskLinks': []
    openWorkflow(nw)

  $('#loadwl').click ->
    $('#uploadfile').click()

  $('#uploadfile').change ->
    loadFile()

  $('#savewl').click ->
    sw =
      'name': workflow.name
      'nodes': workflow.nodes
      'edges': workflow.edges
      'tasks': workflow.tasks
      'taskLinks': workflow.taskLinks || []
    blob = new Blob([JSON.stringify(sw)], {type: 'application/json;charset=utf-8'})
    saveAs(blob, workflow.name+'.json')

  $('#uploadwl').click ->
    d =
        'name': workflow.name
        'operators':
            {
                abstractName: ''
                cost: '0.0'
                description: get_description(n)
                execTime: '0.0'
                input: e.source.name for e in workflow.edges when e.target == n
                isAbstract: is_abstract(n)
                isOperator: is_operator(n)
                isTarget: (e for e in workflow.edges when e.source == n).length == 0
                name: n.name
                output: e.target.name for e in workflow.edges when e.source == n
                status: 'stopped'
            } for n in workflow.nodes
    console.log(JSON.stringify(d))
    $.ajax ires_uri + '/abstractWorkflows/add/' + workflow.name,
        data: JSON.stringify(d)
        type: 'POST'
        contentType: 'application/json; charset=utf-8'
        error: (jqXHR, textStatus, errorThrown) ->
            console.log(jqXHR)
            alert(jqXHR.responseText)

  $('#nodeTitle').on 'input', ->
    $('#wlBoard').find('.node'+nodeSelected).find('text').text($(this).val())
    for node in workflow.nodes
      if parseInt(node.id) == nodeSelected
        node.name = $(this).val()

  $('#taskTitle').on 'input', ->
    $('#tasksBoard').find('.node'+taskSelected).find('text').text($(this).val())
    findTask(taskSelected).name = $(this).val()

  $('#metadataEditor').on 'input', ->
    findTask(taskSelected).operator = JSON.parse($(this).val())

  $('#adddatastore').click ->
    nodeId = workflow.nodes.length
    node =
      'id': nodeId
      'name': ''
      'class': 'circle'
    graph.addNode(node)
    workflow.nodes.push node

  $('#addnode').click ->
    nodeId = workflow.nodes.length
    node =
      'id': nodeId
      'name': ''
    graph.addNode(node)
    workflow.nodes.push node

  $('#removeNode').click ->
    $('#node').addClass('hide')
    graph.removeNode(nodeSelected)
    i = 0
    while i < workflow.edges.length
      if workflow.edges[i]['sourceId'] == nodeSelected or workflow.edges[i]['targetId'] == nodeSelected
        workflow.edges.splice i, 1
      else
        i++
    i = 0
    while i < workflow.tasks.length
      if workflow.tasks[i]['nodeId'] == nodeSelected
        tId = workflow.tasks[i]['id']
        workflow.tasks.splice i, 1
        j = 0
        while j < workflow.taskLinks.length
          if workflow.taskLinks[j]['sourceId'] == tId or workflow.taskLinks[j]['targetId'] == tId
            workflow.taskLinks.splice j, 1
          else
            j++
      else
        i++
    i = 0
    while i < workflow.nodes.length
      if workflow.nodes[i]['id'] == nodeSelected
        workflow.nodes.splice i, 1
      else
        i++
    return

  $('#addlink').click ->
    addingLink = !addingLink
    $('#addlink').parent('li').toggleClass('active')
    nodeLink = false
    taskLink = false
    node1 = null
    node2 = null

  $('#addTask').click ->
    $('#addTask').parent('li').toggleClass('active')
    if not is_operator()
        $('#libraryDatastores').toggleClass('hide')
    else
        $('#libraryOperators').toggleClass('hide')

  $('#createNewDatastore').click ->
      new_task()

  $('#createNewTask').click ->
      new_task()

  $.getJSON ires_uri + '/datasets/json', (json) ->
      $('#libraryDatastores').append("<li><a href='#op-#{op}'>#{op}</a></li>") for op in json
      $('#libraryDatastores').toggleClass('hide')
      $('#libraryDatastores li a[id!=\'createNewDatastore\']').click ->
          $('#addTask').parent('li').removeClass('active')
          $.getJSON ires_uri + '/datasets/json/'+ $(this).text(), (data) ->
              task =
                  'id': workflow.tasks.length
                  'name': data.name
                  'nodeId': nodeSelected
                  'class': 'circle'
                  'type': 'dataset'
                  'isAbstract': false
                  'operator': data
              tgraph.addNode(task)
              workflow.tasks.push task
              update_name(data.name)

  $.getJSON ires_uri + '/abstractOperators/json', (json) ->
      $('#libraryOperators').append("<li><a href='#op-#{op}'>#{op}</a></li>") for op in json
      $('#libraryOperators li a[id!=\'createNewTask\']').click ->
          $('#libraryOperators').toggleClass('hide')
          $('#addTask').parent('li').removeClass('active')
          $.getJSON ires_uri + '/abstractOperators/json/'+ $(this).text(), (data) ->
              task =
                  'id': workflow.tasks.length
                  'name': data.name
                  'nodeId': nodeSelected
                  'class': 'rect'
                  'operator': data
              tgraph.addNode(task)
              workflow.tasks.push task
              update_name(data.name)

  $('#analyse').click ->
    $.ajax '/php/index.php',
      data:
        action: 'analyse'
        workflow:
          'name': workflow.name
          'nodes': workflow.nodes
          'edges': workflow.edges
          'tasks': workflow.tasks
          'taskLinks': workflow.taskLinks || []
      type: 'POST'
      success: (data, textStatus, jqXHR) ->
#        console.log(data)
        newWorkflow = JSON.parse(data)
        newWorkflow.taskLinks = newWorkflow.taskLinks || []
#        commented out until better times
        openWorkflow(newWorkflow)
      error: (jqXHR, textStatus, errorThrown) ->
        console.log(jqXHR)
        alert(jqXHR.responseText)

  $('#optimise').click ->
    $.ajax '/php/index.php',
      data:
        action: 'optimise'
        workflow:
          'name': workflow.name
          'nodes': workflow.nodes
          'edges': workflow.edges
          'tasks': workflow.tasks
          'taskLinks': workflow.taskLinks || []
      type: 'POST'
      success: (data, textStatus, jqXHR) ->
#        console.log(data)
        newWorkflow = JSON.parse(data)
        newWorkflow.taskLinks = newWorkflow.taskLinks || []
        openWorkflow(newWorkflow)
      error: (jqXHR, textStatus, errorThrown) ->
        console.log(jqXHR)
        alert(jqXHR.responseText)

  $('#execute').click ->
    $.ajax '/php/index.php',
      data:
        action: 'execute'
        workflow:
          'name': workflow.name
          'nodes': workflow.nodes
          'edges': workflow.edges
          'tasks': workflow.tasks
          'taskLinks': workflow.taskLinks || []
      type: 'POST'
      success: (data, textStatus, jqXHR) ->
        console.log(data)
      error: (jqXHR, textStatus, errorThrown) ->
        console.log(jqXHR)
        alert(jqXHR.responseText)

  $('#dashboard').click ->
    $.ajax '/php/index.php',
      data:
        action: 'get_list'
      type: 'POST'
      success: (data, textStatus, jqXHR) ->
        console.log(data)
      error: (jqXHR, textStatus, errorThrown) ->
        console.log(textStatus)

$.getJSON 'workflows/test_wl.json', (json) ->
  openWorkflow(json)

graph = new wGraph('#wlBoard')

tgraph = new wGraph('#tasksBoard')
