workflow = null

nodeSelected = null
taskSelected = null

addingLink = false
node1 = null
node2 = null
nodeLink = false
taskLink = false

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
    task = workflow.tasks[id]
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

  $('#nodeTitle').on 'input', ->
    $('#wlBoard').find('.node'+nodeSelected).find('text').text($(this).val())
    for node in workflow.nodes
      if parseInt(node.id) == nodeSelected
        node.name = $(this).val()

  $('#taskTitle').on 'input', ->
    $('#tasksBoard').find('.node'+taskSelected).find('text').text($(this).val())
    workflow.tasks[taskSelected].name = $(this).val()

  $('#metadataEditor').on 'input', ->
    workflow.tasks[taskSelected].operator = JSON.parse($(this).val())

  $('#adddatastore').click ->
    nodeName = prompt('Please enter datastore name', '')
    nodeId = workflow.nodes.length
    node =
      'id': nodeId
      'name': nodeName
      'class': 'circle'
    graph.addNode(node)
    workflow.nodes.push node

  $('#addnode').click ->
    nodeName = prompt('Please enter node name', '')
    nodeId = workflow.nodes.length
    node =
      'id': nodeId
      'name': nodeName
    graph.addNode(node)
    workflow.nodes.push node

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

  $('#filterJoin').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'Filter Join'
      'nodeId': nodeSelected
      'class': 'circle'
      'operators':
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
  $('#PeakDetection').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'PeakDetection'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'name': 'PeakDetection'
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
  $('#kMeans').click ->
    $('#libraryOperators').toggleClass('hide')
    $('#addTask').parent('li').removeClass('active')
    taskId = workflow.tasks.length
    task =
      'id': taskId
      'name': 'k-Means'
      'nodeId': nodeSelected
      'class': 'circle'
      'operator':
        'constraints':
          'input': 'number': 1
          'output': 'number': 1
          'opSpecification':
            'algorithm': 'name': 'k-means'
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
        'constraints': {}
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
        console.log(textStatus)

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
        console.log(textStatus)

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
        console.log(textStatus)

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
