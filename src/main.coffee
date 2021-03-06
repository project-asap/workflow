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

tabContent = []

nodeSelected = null
taskSelected = null

addingLink = false
node1 = null
node2 = null
nodeLink = false
taskLink = false
wasExecuted = false

openWorkflow = (w) ->
  workflow = w

  graph.clean()
  $('#node').addClass('hide')
  $('#taskName').addClass('hide')
  $('#metadata').addClass('hide')
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

    tabContent.push({
      'name': newWorkflow['name']
      'wl': newWorkflow
    })
    $('#tabs ul li').removeClass('active')
    lit = '<li class="active"><a href="#">'+newWorkflow['name']+'</a></li>'
    $('#tabs ul').append(lit)

    openWorkflow(newWorkflow)
    $('#uploadfile').replaceWith( $('#uploadfile').clone(true) )
  fr.readAsText(file)

selectNode = (id, type) ->
  $('#node').removeClass('hide')
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
        newclass = oldclass.replace('selected', '')
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

$(document).ready ->
  $('#newwl').click ->
    wlName = prompt('Please enter workflow name', '')
    nw =
      'name': wlName
      'nodes': []
      'edges': []
      'tasks': []
      'taskLinks': []

    tabContent.push({
      'name': wlName
      'wl': nw
    })
    $('#tabs ul li').removeClass('active')
    lit = '<li class="active"><a href="#">'+wlName+'</a></li>'
    $('#tabs ul').append(lit)

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
    nodeName = prompt('Please enter datastore name', '')
    nodeId = workflow.nodes.length
    node =
      'id': nodeId
      'name': nodeName
      'class': 'circle'
    graph.addNode(node)
    workflow.nodes.push node
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'type': 'dataset'
      'name': 'dataset'
      'nodeId': nodeId
      'class': 'circle'
      'operator':
        'constraints':
          'engine': 'FS': 'HDFS'
        'execution': 'path': 'hdfs:///dataset_simulated/06/1.csv'
        'optimization': 'size': '1E9'
    tgraph.addNode(task)
    workflow.tasks.push task


  $('#addnode').click ->
    nodeName = prompt('Please enter node name', '')
    nodeId = workflow.nodes.length
    node =
      'id': nodeId
      'name': nodeName
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
    $('#libraryOperators').toggleClass('hide')

  $('#createNewTask').click ->
    nodeName = prompt('Please enter task name', '')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': nodeName
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':{}
    tgraph.addNode(task)
    workflow.tasks.push task

  $('#mpBar').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'mp_bar'
      'nodeId': nodeSelected
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'bar_chart'
    tgraph.addNode(task)
    workflow.tasks.push task

  $('#mpPie').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'mp_pie'
      'nodeId': nodeSelected
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'pie_chart'
    tgraph.addNode(task)
    workflow.tasks.push task

  $('#mpGeo').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'mp_geo'
      'nodeId': nodeSelected
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'geo_map'
    tgraph.addNode(task)
    workflow.tasks.push task

  $('#rp').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'rp'
      'nodeId': nodeSelected
      'operator':
        'constraints': {}
    tgraph.addNode(task)
    workflow.tasks.push task

  $('#ifElse').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'if-else'
      'nodeId': nodeSelected
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 2
          'opSpecification':
            'algorithm': 'if-else'
    tgraph.addNode(task)
    workflow.tasks.push task

  $('#gotoL').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'gotoL'
      'nodeId': nodeSelected
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 2
          'opSpecification':
            'algorithm': 'gotoL'
    tgraph.addNode(task)
    workflow.tasks.push task

  $('#gotoP').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'gotoP'
      'nodeId': nodeSelected
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'gotoP'
    tgraph.addNode(task)
    workflow.tasks.push task

  $('#filterJoin').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'Filter Join'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 2
          'input0': 'type': 'SQL'
          'input1': 'type': 'SQL'
          'output': 'number': 1
          'output0': 'type': 'SQL'
          'opSpecification':
            'algorithm': 'name': 'SQL_query'
            'SQL_query': 'SELECT NATIONKEY, TOTALPRICE FROM $1 LEFT JOIN $2 ON $1.CUSTKEY=$2.CUSTKEY'
    tgraph.addNode(task)
    workflow.tasks.push task
  $('#groupBySort').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'groupBy Sort'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 1
          'input0': 'type': 'SQL'
          'output': 'number': 1
          'output0': 'type': 'SQL'
          'opSpecification':
            'algorithm': 'name': 'SQL_query'
            'SQL_query': 'SELECT NATIONKEY, SUM(TOTALPRICE) AS SUM FROM $1 GROUP BY NATIONKEY ORDER BY SUM'
    tgraph.addNode(task)
    workflow.tasks.push task
  $('#WindPeakDetection').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'Wind_Peak_Detection'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 2
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'name': 'Wind_Peak_Detection'
    tgraph.addNode(task)
    workflow.tasks.push task
  $('#WindUserProfiling').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'Wind_User_Profiling'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'name': 'Wind_User_Profiling'
    tgraph.addNode(task)
    workflow.tasks.push task
  $('#WindPeakDetectionPublisher').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'Wind_Peak_Detection_Publisher'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'name': 'Wind_Peak_Detection_Publisher'
    tgraph.addNode(task)
    workflow.tasks.push task
  $('#WindSpatioTemporalAggregation').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'Wind_Spatio_Temporal_Aggregation'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'name': 'Wind_Spatio_Temporal_Aggregation'
    tgraph.addNode(task)
    workflow.tasks.push task
  $('#WindStatisticsPublisher').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'Wind_Statistics_Publisher'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'name': 'Wind_Statistics_Publisher'
    tgraph.addNode(task)
    workflow.tasks.push task
  $('#WindDistributionComputation').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'Wind_Distribution_Computation'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'name': 'Wind_Distribution_Computation'
    tgraph.addNode(task)
    workflow.tasks.push task
  $('#WindDataFilter').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'Wind_Data_Filter'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'name': 'Wind_Data_Filter'
    tgraph.addNode(task)
    workflow.tasks.push task
  $('#WindStereotypeClassification').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'Wind_Stereotype_Classification'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'name': 'Wind_Stereotype_Classification'
    tgraph.addNode(task)
    workflow.tasks.push task
  $('#tfIdf').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'Tf-Idf'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'name': 'TF_IDF'
    tgraph.addNode(task)
    workflow.tasks.push task
  $('#WindKmeans').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'Wind_Kmeans'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'name': 'Wind_Kmeans'
    tgraph.addNode(task)
    workflow.tasks.push task

  $('#filter').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'filter'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 1
          'input0': 'type': 'SQL'
          'output': 'number': 1
          'output0': 'type': 'SQL'
          'opSpecification':
            'algorithm': 'name': 'SQL_query'
            'SQL_query': 'SELECT * WHERE $filter_exp FROM $1'
    tgraph.addNode(task)
    workflow.tasks.push task

  $('#calc').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'calc'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 1
          'input0': 'type': 'SQL'
          'output': 'number': 1
          'output0': 'type': 'SQL'
          'opSpecification':
            'algorithm': 'name': 'SQL_query'
            'SQL_query': 'SELECT *, $calc_key = $calc_exp FROM $1'
    tgraph.addNode(task)
    workflow.tasks.push task

  $('#dataset').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'dataset'
      'nodeId': nodeSelected
      'class': 'circle'
      'type': 'dataset'
      'operator':
        'constraints':
          'constraints':
            'engine': 'FS': 'HDFS'
        'execution': 'path': 'hdfs:///dataset_simulated/06/1.csv'
        'optimization': 'size': '1E9'
    tgraph.addNode(task)
    workflow.tasks.push task

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

  $('#optimiseAll').click ->
    $.ajax '/php/index.php',
      data:
        action: 'optimiseAll'
        workflows: tabContent
      type: 'POST'
      success: (data, textStatus, jqXHR) ->
        console.log(data)
        $.getJSON data['workflow'], (json) ->
          $('#tabs ul li').removeClass('active')
          tabContent.push({
            'name': json['name']
            'wl': json
          })
          lit = '<li class="active"><a href="#">'+json['name']+'</a></li>'
          $('#tabs ul').append(lit)

          openWorkflow(json)
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

  $('#tabs').on
    click: ->
      $('#tabs ul li').removeClass('active')
      $(this).parent('li').addClass('active')
      itab = $(this).parent('li').index()
      openWorkflow(tabContent[itab]['wl'])
    'ul > li > a'

#$.getJSON 'workflows/test_wl.json', (json) ->
#  tabContent.push({
#    'name': json['name']
#    'wl': json
#  })
#  lit = '<li class="active"><a href="#">'+json['name']+'</a></li>'
#  $('#tabs ul').append(lit)
#  openWorkflow(json)

showChart = (dpoints) ->
  chart = new CanvasJS.Chart('chartContainer',
    {
      theme: "theme2"
      title: {text: "mp_bar"}
      animationEnabled: false
      data: [{
        type: "column"
        dataPoints: dpoints
        }]
    })

  chart.render()

graph = new wGraph('#wlBoard')

tgraph = new wGraph('#tasksBoard')
