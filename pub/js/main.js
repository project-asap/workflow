var addingLink, graph, loadFile, node1, node2, nodeLink, nodeSelected, openWorkflow, selectNode, showTasks, taskLink, taskSelected, tgraph, workflow;

workflow = null;

nodeSelected = null;

taskSelected = null;

addingLink = false;

node1 = null;

node2 = null;

nodeLink = false;

taskLink = false;

openWorkflow = function(w) {
  var i, j, len, len1, link, node, ref, ref1;
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
  for (i = 0, len = ref.length; i < len; i++) {
    node = ref[i];
    graph.addNode(node);
  }
  ref1 = w.links;
  for (j = 0, len1 = ref1.length; j < len1; j++) {
    link = ref1[j];
    graph.addLink(link);
  }
};

showTasks = function(nodeId) {
  var i, j, len, len1, link, ref, ref1, task;
  tgraph.clean();
  ref = workflow.tasks;
  for (i = 0, len = ref.length; i < len; i++) {
    task = ref[i];
    if (parseInt(task.nodeId) === nodeId) {
      tgraph.addNode(task);
    }
  }
  ref1 = workflow.taskLinks;
  for (j = 0, len1 = ref1.length; j < len1; j++) {
    link = ref1[j];
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
  var link, newclass, node, oldclass, task;
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
    task = workflow.tasks[id];
    $('#taskTitle').val(task.name);
    $('#metadataEditor').val(JSON.stringify(task.json, null, 2));
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
          'id': graph.links.length
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
    node = workflow.nodes[id];
    showTasks(id);
    $('#nodeTitle').val(node.name);
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
          'id': graph.links.length
        };
        graph.addLink(link);
        workflow.links.push(link);
        nodeLink = false;
        node1 = null;
        return node2 = null;
      }
    }
  }
};

$(document).ready(function() {
  $('#newwl').click(function() {
    var nw;
    nw = {
      'nodes': [],
      'links': [],
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
      'nodes': workflow.nodes,
      'links': workflow.links,
      'tasks': workflow.tasks,
      'taskLinks': workflow.taskLinks || []
    };
    blob = new Blob([JSON.stringify(sw)], {
      type: 'application/json;charset=utf-8'
    });
    return saveAs(blob, 'workflow.json');
  });
  $('#nodeTitle').on('input', function() {
    $('#wlBoard').find('.node' + nodeSelected).find('text').text($(this).val());
    return workflow.nodes[nodeSelected].name = $(this).val();
  });
  $('#taskTitle').on('input', function() {
    $('#tasksBoard').find('.node' + taskSelected).find('text').text($(this).val());
    return workflow.tasks[taskSelected].name = $(this).val();
  });
  $('#metadataEditor').on('input', function() {
    return workflow.tasks[taskSelected].json = JSON.parse($(this).val());
  });
  $('#adddatastore').click(function() {
    var node, nodeId, nodeName;
    nodeName = prompt('Please enter datastore name', '');
    nodeId = workflow.nodes.length;
    node = {
      'id': nodeId,
      'name': nodeName,
      'class': 'circle'
    };
    graph.addNode(node);
    return workflow.nodes.push(node);
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
      'json': {}
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#filterJoin').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'Filter Join',
      'nodeId': nodeSelected,
      'class': 'circle',
      'json': {
        'constraints': {
          'input': {
            'number': 2
          },
          'input0': {
            'type': 'SQL'
          },
          'input1': {
            'type': 'SQL'
          },
          'output': {
            'number': 1
          },
          'output0': {
            'type': 'SQL'
          },
          'opSpecification': {
            'algorithm': {
              'name': 'SQL_query'
            },
            'SQL_query': 'SELECT NATIONKEY, TOTALPRICE FROM $1 LEFT JOIN $2 ON $1.CUSTKEY=$2.CUSTKEY'
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#groupBySort').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'groupBy Sort',
      'nodeId': nodeSelected,
      'class': 'circle',
      'json': {
        'constraints': {
          'input': {
            'number': 1
          },
          'input0': {
            'type': 'SQL'
          },
          'output': {
            'number': 1
          },
          'output0': {
            'type': 'SQL'
          },
          'opSpecification': {
            'algorithm': {
              'name': 'SQL_query'
            },
            'SQL_query': 'SELECT NATIONKEY, SUM(TOTALPRICE) AS SUM FROM $1 GROUP BY NATIONKEY ORDER BY SUM'
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#PeakDetection').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'PeakDetection',
      'nodeId': nodeSelected,
      'class': 'circle',
      'json': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': {
              'name': 'PeakDetection'
            }
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#tfIdf').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'Tf-Idf',
      'nodeId': nodeSelected,
      'class': 'circle',
      'json': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': {
              'name': 'TF_IDF'
            }
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#kMeans').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'k-Means',
      'nodeId': nodeSelected,
      'class': 'circle',
      'json': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': {
              'name': 'k-means'
            }
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#filter').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'filter',
      'nodeId': nodeSelected,
      'class': 'circle',
      'json': {
        'constraints': {
          'input': {
            'number': 1
          },
          'input0': {
            'type': 'SQL'
          },
          'output': {
            'number': 1
          },
          'output0': {
            'type': 'SQL'
          },
          'opSpecification': {
            'algorithm': {
              'name': 'SQL_query'
            },
            'SQL_query': 'SELECT * WHERE $filter_exp FROM $1'
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#calc').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'calc',
      'nodeId': nodeSelected,
      'class': 'circle',
      'json': {
        'constraints': {
          'input': {
            'number': 1
          },
          'input0': {
            'type': 'SQL'
          },
          'output': {
            'number': 1
          },
          'output0': {
            'type': 'SQL'
          },
          'opSpecification': {
            'algorithm': {
              'name': 'SQL_query'
            },
            'SQL_query': 'SELECT *, $calc_key = $calc_exp FROM $1'
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#analyse').click(function() {
    return $.ajax('/php/index.php', {
      data: {
        action: 'analyse',
        workflow: {
          'nodes': workflow.nodes,
          'links': workflow.links,
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
        return console.log(textStatus);
      }
    });
  });
  return $('#optimise').click(function() {
    return $.ajax('/php/index.php', {
      data: {
        action: 'optimise',
        workflow: {
          'nodes': workflow.nodes,
          'links': workflow.links,
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
        return console.log(textStatus);
      }
    });
  });
});

$.getJSON('files/workflow.json', function(json) {
  return openWorkflow(json);
});

graph = new wGraph('#wlBoard');

tgraph = new wGraph('#tasksBoard');
