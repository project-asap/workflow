var addingLink, findTask, graph, loadFile, node1, node2, nodeLink, nodeSelected, openWorkflow, selectNode, showTasks, taskLink, taskSelected, tgraph, workflow;

workflow = null;

nodeSelected = null;

taskSelected = null;

addingLink = false;

node1 = null;

node2 = null;

nodeLink = false;

taskLink = false;

openWorkflow = function(w) {
  var edge, k, l, len, len1, node, ref, ref1;
  workflow = w;
  graph.clean();
  $('#node').addClass('hide');
  $('#taskName').addClass('hide');
  $('#metadata').addClass('hide');
  $('#libraryOperators').addClass('hide');
  $('#addlink').parent('li').removeClass('active');
  $('#addTask').parent('li').removeClass('active');
  addingLink = false;
  ref = w.nodes;
  for (k = 0, len = ref.length; k < len; k++) {
    node = ref[k];
    graph.addNode(node);
  }
  ref1 = w.edges;
  for (l = 0, len1 = ref1.length; l < len1; l++) {
    edge = ref1[l];
    graph.addLink(edge);
  }
};

findTask = function(taskId) {
  var k, len, ref, task;
  ref = workflow.tasks;
  for (k = 0, len = ref.length; k < len; k++) {
    task = ref[k];
    if (parseInt(task.id) === taskId) {
      return task;
    }
  }
};

showTasks = function(nodeId) {
  var k, l, len, len1, link, ref, ref1, task;
  tgraph.clean();
  ref = workflow.tasks;
  for (k = 0, len = ref.length; k < len; k++) {
    task = ref[k];
    if (parseInt(task.nodeId) === nodeId) {
      tgraph.addNode(task);
    }
  }
  ref1 = workflow.taskLinks;
  for (l = 0, len1 = ref1.length; l < len1; l++) {
    link = ref1[l];
    tgraph.addLink(link);
  }
};

loadFile = function() {
  var file, fr, input;
  input = $('#uploadfile')[0];
  file = input.files[0];
  fr = new FileReader();
  fr.onload = function(e) {
    var lines, newWorkflow;
    lines = e.target.result;
    newWorkflow = JSON.parse(lines);
    openWorkflow(newWorkflow);
    return $('#uploadfile').replaceWith($('#uploadfile').clone(true));
  };
  return fr.readAsText(file);
};

selectNode = function(id, type) {
  var k, len, link, newclass, node, oldclass, ref, task;
  $('#node').removeClass('hide');
  if (type === 'task') {
    $('#taskName').removeClass('hide');
    $('#metadata').removeClass('hide');
    if (!isNaN(parseInt(taskSelected))) {
      oldclass = $('#tasksBoard').find('.node' + taskSelected).attr('class');
      if (!!oldclass) {
        newclass = oldclass.replace('selected', '');
        $('#tasksBoard').find('.node' + taskSelected).attr('class', newclass);
      }
    }
    taskSelected = id;
    oldclass = $('#tasksBoard').find('.node' + taskSelected).attr('class');
    $('#tasksBoard').find('.node' + taskSelected).attr('class', oldclass + ' selected');
    task = findTask(id);
    $('#taskTitle').val(task.name);
    $('#metadataEditor').val(JSON.stringify(task.operator, null, 2));
    if (addingLink) {
      if (nodeLink || isNaN(parseInt(node1))) {
        taskLink = true;
        nodeLink = false;
        node1 = taskSelected;
        node2 = null;
      }
      if (!isNaN(parseInt(node1)) && node1 !== taskSelected) {
        node2 = taskSelected;
        link = {
          'sourceId': node1,
          'targetId': node2,
          'id': workflow.taskLinks.length
        };
        tgraph.addLink(link);
        workflow.taskLinks.push(link);
        taskLink = false;
        node1 = null;
        return node2 = null;
      }
    }
  } else {
    $('#taskName').addClass('hide');
    $('#metadata').addClass('hide');
    if (!isNaN(parseInt(nodeSelected))) {
      oldclass = $('#wlBoard').find('.node' + nodeSelected).attr('class');
      if (!!oldclass) {
        newclass = oldclass.replace('selected', '');
        $('#wlBoard').find('.node' + nodeSelected).attr('class', newclass);
      }
    }
    nodeSelected = id;
    oldclass = $('#wlBoard').find('.node' + nodeSelected).attr('class');
    $('#wlBoard').find('.node' + nodeSelected).attr('class', oldclass + ' selected');
    ref = workflow.nodes;
    for (k = 0, len = ref.length; k < len; k++) {
      node = ref[k];
      if (parseInt(node.id) === id) {
        $('#nodeTitle').val(node.name);
      }
    }
    showTasks(id);
    if (addingLink) {
      if (taskLink || isNaN(parseInt(node1))) {
        taskLink = false;
        nodeLink = true;
        node1 = nodeSelected;
        node2 = null;
      }
      if (!isNaN(parseInt(node1)) && node1 !== nodeSelected) {
        node2 = nodeSelected;
        link = {
          'sourceId': node1,
          'targetId': node2,
          'id': workflow.edges.length
        };
        graph.addLink(link);
        workflow.edges.push(link);
        nodeLink = false;
        node1 = null;
        return node2 = null;
      }
    }
  }
};

$(document).ready(function() {
  $('#newwl').click(function() {
    var nw, wlName;
    wlName = prompt('Please enter workflow name', '');
    nw = {
      'name': wlName,
      'nodes': [],
      'edges': [],
      'tasks': [],
      'taskLinks': []
    };
    return openWorkflow(nw);
  });
  $('#loadwl').click(function() {
    return $('#uploadfile').click();
  });
  $('#uploadfile').change(function() {
    return loadFile();
  });
  $('#savewl').click(function() {
    var blob, sw;
    sw = {
      'name': workflow.name,
      'nodes': workflow.nodes,
      'edges': workflow.edges,
      'tasks': workflow.tasks,
      'taskLinks': workflow.taskLinks || []
    };
    blob = new Blob([JSON.stringify(sw)], {
      type: 'application/json;charset=utf-8'
    });
    return saveAs(blob, workflow.name + '.json');
  });
  $('#nodeTitle').on('input', function() {
    var k, len, node, ref, results;
    $('#wlBoard').find('.node' + nodeSelected).find('text').text($(this).val());
    ref = workflow.nodes;
    results = [];
    for (k = 0, len = ref.length; k < len; k++) {
      node = ref[k];
      if (parseInt(node.id) === nodeSelected) {
        results.push(node.name = $(this).val());
      } else {
        results.push(void 0);
      }
    }
    return results;
  });
  $('#taskTitle').on('input', function() {
    $('#tasksBoard').find('.node' + taskSelected).find('text').text($(this).val());
    return findTask(taskSelected).name = $(this).val();
  });
  $('#metadataEditor').on('input', function() {
    return findTask(taskSelected).operator = JSON.parse($(this).val());
  });
  $('#adddatastore').click(function() {
    var node, nodeId, nodeName, task, taskId;
    nodeName = prompt('Please enter datastore name', '');
    nodeId = workflow.nodes.length;
    node = {
      'id': nodeId,
      'name': nodeName,
      'class': 'circle'
    };
    graph.addNode(node);
    workflow.nodes.push(node);
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'type': 'dataset',
      'name': 'dataset',
      'nodeId': nodeId,
      'class': 'circle',
      'operator': {
        'constraints': {
          'engine': {
            'FS': 'HDFS'
          }
        },
        'execution': {
          'path': 'hdfs:///dataset_simulated/06/1.csv'
        },
        'optimization': {
          'size': '1E9'
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#addnode').click(function() {
    var node, nodeId, nodeName;
    nodeName = prompt('Please enter node name', '');
    nodeId = workflow.nodes.length;
    node = {
      'id': nodeId,
      'name': nodeName
    };
    graph.addNode(node);
    return workflow.nodes.push(node);
  });
  $('#removeNode').click(function() {
    var i, j, tId;
    $('#node').addClass('hide');
    graph.removeNode(nodeSelected);
    i = 0;
    while (i < workflow.edges.length) {
      if (workflow.edges[i]['sourceId'] === nodeSelected || workflow.edges[i]['targetId'] === nodeSelected) {
        workflow.edges.splice(i, 1);
      } else {
        i++;
      }
    }
    i = 0;
    while (i < workflow.tasks.length) {
      if (workflow.tasks[i]['nodeId'] === nodeSelected) {
        tId = workflow.tasks[i]['id'];
        workflow.tasks.splice(i, 1);
        j = 0;
        while (j < workflow.taskLinks.length) {
          if (workflow.taskLinks[j]['sourceId'] === tId || workflow.taskLinks[j]['targetId'] === tId) {
            workflow.taskLinks.splice(j, 1);
          } else {
            j++;
          }
        }
      } else {
        i++;
      }
    }
    i = 0;
    while (i < workflow.nodes.length) {
      if (workflow.nodes[i]['id'] === nodeSelected) {
        workflow.nodes.splice(i, 1);
      } else {
        i++;
      }
    }
  });
  $('#addlink').click(function() {
    addingLink = !addingLink;
    $('#addlink').parent('li').toggleClass('active');
    nodeLink = false;
    taskLink = false;
    node1 = null;
    return node2 = null;
  });
  $('#addTask').click(function() {
    $('#addTask').parent('li').toggleClass('active');
    return $('#libraryOperators').toggleClass('hide');
  });
  $('#createNewTask').click(function() {
    var nodeName, task, taskId;
    nodeName = prompt('Please enter task name', '');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': nodeName,
      'nodeId': nodeSelected,
      'class': 'circle',
      'operator': {
        'constraints': {}
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $.getJSON('http://localhost:1323/abstractOperators/json', function(json) {
    var k, len, op;
    for (k = 0, len = json.length; k < len; k++) {
      op = json[k];
      $('#libraryOperators').append("<li><a href='#op-" + op + "'>" + op + "</a></li>");
    }
    return $('#libraryOperators li a[id!=\'createNewTask\']').click(function() {
      console.log($('#libraryOperators li a').length);
      $('#libraryOperators').toggleClass('hide');
      $('#addTask').parent('li').removeClass('active');
      return $.getJSON('http://localhost:1323/abstractOperators/json/' + $(this).text(), function(data) {
        var task;
        console.log(data);
        task = {
          'id': workflow.tasks.length,
          'name': data.name,
          'nodeId': nodeSelected,
          'class': 'rect',
          'operator': data
        };
        console.log(task);
        tgraph.addNode(task);
        return workflow.tasks.push(task);
      });
    });
  });
  $('#analyse').click(function() {
    return $.ajax('/php/index.php', {
      data: {
        action: 'analyse',
        workflow: {
          'name': workflow.name,
          'nodes': workflow.nodes,
          'edges': workflow.edges,
          'tasks': workflow.tasks,
          'taskLinks': workflow.taskLinks || []
        }
      },
      type: 'POST',
      success: function(data, textStatus, jqXHR) {
        var newWorkflow;
        newWorkflow = JSON.parse(data);
        newWorkflow.taskLinks = newWorkflow.taskLinks || [];
        return openWorkflow(newWorkflow);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log(jqXHR);
        return alert(jqXHR.responseText);
      }
    });
  });
  $('#optimise').click(function() {
    return $.ajax('/php/index.php', {
      data: {
        action: 'optimise',
        workflow: {
          'name': workflow.name,
          'nodes': workflow.nodes,
          'edges': workflow.edges,
          'tasks': workflow.tasks,
          'taskLinks': workflow.taskLinks || []
        }
      },
      type: 'POST',
      success: function(data, textStatus, jqXHR) {
        var newWorkflow;
        newWorkflow = JSON.parse(data);
        newWorkflow.taskLinks = newWorkflow.taskLinks || [];
        return openWorkflow(newWorkflow);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log(jqXHR);
        return alert(jqXHR.responseText);
      }
    });
  });
  $('#execute').click(function() {
    return $.ajax('/php/index.php', {
      data: {
        action: 'execute',
        workflow: {
          'name': workflow.name,
          'nodes': workflow.nodes,
          'edges': workflow.edges,
          'tasks': workflow.tasks,
          'taskLinks': workflow.taskLinks || []
        }
      },
      type: 'POST',
      success: function(data, textStatus, jqXHR) {
        return console.log(data);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log(jqXHR);
        return alert(jqXHR.responseText);
      }
    });
  });
  return $('#dashboard').click(function() {
    return $.ajax('/php/index.php', {
      data: {
        action: 'get_list'
      },
      type: 'POST',
      success: function(data, textStatus, jqXHR) {
        return console.log(data);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        return console.log(textStatus);
      }
    });
  });
});

$.getJSON('workflows/test_wl.json', function(json) {
  return openWorkflow(json);
});

graph = new wGraph('#wlBoard');

tgraph = new wGraph('#tasksBoard');
