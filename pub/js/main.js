var addingLink, findTask, graph, loadFile, node1, node2, nodeLink, nodeSelected, openWorkflow, selectNode, showChart, showTasks, tabContent, taskLink, taskSelected, tgraph, wasExecuted, workflow;

workflow = null;

tabContent = [];

nodeSelected = null;

taskSelected = null;

addingLink = false;

node1 = null;

node2 = null;

nodeLink = false;

taskLink = false;

wasExecuted = false;

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
    var lines, lit, newWorkflow;
    lines = e.target.result;
    newWorkflow = JSON.parse(lines);
    tabContent.push({
      'name': newWorkflow['name'],
      'wl': newWorkflow
    });
    $('#tabs ul li').removeClass('active');
    lit = '<li class="active"><a href="#">' + newWorkflow['name'] + '</a></li>';
    $('#tabs ul').append(lit);
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
    var lit, nw, wlName;
    wlName = prompt('Please enter workflow name', '');
    nw = {
      'name': wlName,
      'nodes': [],
      'edges': [],
      'tasks': [],
      'taskLinks': []
    };
    tabContent.push({
      'name': wlName,
      'wl': nw
    });
    $('#tabs ul li').removeClass('active');
    lit = '<li class="active"><a href="#">' + wlName + '</a></li>';
    $('#tabs ul').append(lit);
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
  $('#mpBar').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'mp_bar',
      'nodeId': nodeSelected,
      'operator': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': 'bar_chart'
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#mpPie').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'mp_pie',
      'nodeId': nodeSelected,
      'operator': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': 'pie_chart'
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#mpGeo').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'mp_geo',
      'nodeId': nodeSelected,
      'operator': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': 'geo_map'
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#rp').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'rp',
      'nodeId': nodeSelected,
      'operator': {
        'constraints': {}
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#ifElse').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'if-else',
      'nodeId': nodeSelected,
      'operator': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 2
          },
          'opSpecification': {
            'algorithm': 'if-else'
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#gotoL').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'gotoL',
      'nodeId': nodeSelected,
      'operator': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 2
          },
          'opSpecification': {
            'algorithm': 'gotoL'
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#gotoP').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'gotoP',
      'nodeId': nodeSelected,
      'operator': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': 'gotoP'
          }
        }
      }
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
      'operator': {
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
      'operator': {
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
  $('#WindPeakDetection').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'Wind_Peak_Detection',
      'nodeId': nodeSelected,
      'class': 'circle',
      'operator': {
        'constraints': {
          'input': {
            'number': 2
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': {
              'name': 'Wind_Peak_Detection'
            }
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#WindUserProfiling').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'Wind_User_Profiling',
      'nodeId': nodeSelected,
      'class': 'circle',
      'operator': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': {
              'name': 'Wind_User_Profiling'
            }
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#WindPeakDetectionPublisher').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'Wind_Peak_Detection_Publisher',
      'nodeId': nodeSelected,
      'class': 'circle',
      'operator': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': {
              'name': 'Wind_Peak_Detection_Publisher'
            }
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#WindSpatioTemporalAggregation').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'Wind_Spatio_Temporal_Aggregation',
      'nodeId': nodeSelected,
      'class': 'circle',
      'operator': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': {
              'name': 'Wind_Spatio_Temporal_Aggregation'
            }
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#WindStatisticsPublisher').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'Wind_Statistics_Publisher',
      'nodeId': nodeSelected,
      'class': 'circle',
      'operator': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': {
              'name': 'Wind_Statistics_Publisher'
            }
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#WindDistributionComputation').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'Wind_Distribution_Computation',
      'nodeId': nodeSelected,
      'class': 'circle',
      'operator': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': {
              'name': 'Wind_Distribution_Computation'
            }
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#WindDataFilter').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'Wind_Data_Filter',
      'nodeId': nodeSelected,
      'class': 'circle',
      'operator': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': {
              'name': 'Wind_Data_Filter'
            }
          }
        }
      }
    };
    tgraph.addNode(task);
    return workflow.tasks.push(task);
  });
  $('#WindStereotypeClassification').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'Wind_Stereotype_Classification',
      'nodeId': nodeSelected,
      'class': 'circle',
      'operator': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': {
              'name': 'Wind_Stereotype_Classification'
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
      'operator': {
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
  $('#WindKmeans').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'Wind_Kmeans',
      'nodeId': nodeSelected,
      'class': 'circle',
      'operator': {
        'constraints': {
          'input': {
            'number': 1
          },
          'output': {
            'number': 1
          },
          'opSpecification': {
            'algorithm': {
              'name': 'Wind_Kmeans'
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
      'operator': {
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
      'operator': {
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
  $('#dataset').click(function() {
    var task, taskId;
    $('#libraryOperators').toggleClass('hide');
    $('#addTask').parent('li').removeClass('active');
    taskId = workflow.tasks.length;
    task = {
      'id': taskId,
      'name': 'dataset',
      'nodeId': nodeSelected,
      'class': 'circle',
      'type': 'dataset',
      'operator': {
        'constraints': {
          'constraints': {
            'engine': {
              'FS': 'HDFS'
            }
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
  $('#optimiseAll').click(function() {
    return $.ajax('/php/index.php', {
      data: {
        action: 'optimiseAll',
        workflows: tabContent
      },
      type: 'POST',
      success: function(data, textStatus, jqXHR) {
        console.log(data);
        return $.getJSON(data['workflow'], function(json) {
          var lit;
          $('#tabs ul li').removeClass('active');
          tabContent.push({
            'name': json['name'],
            'wl': json
          });
          lit = '<li class="active"><a href="#">' + json['name'] + '</a></li>';
          $('#tabs ul').append(lit);
          return openWorkflow(json);
        });
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log(jqXHR);
        return alert(jqXHR.responseText);
      }
    });
  });
  $('#execute').click(function() {
    // TODO: increment list of abstract workflows
    id = 100;
    // TODO: use config params of IRES server
    // TODO: check workflow format
    $.ajax('http://localhost:1323/abstractWorkflows/add/'+id+'/', {
      workflow: workflow,
      type: 'POST',
      success: function(data, textStatus, jqXHR) {
        return console.log(data);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log(jqXHR);
        return alert(jqXHR.responseText);
      }
    });

    $.ajax('http://localhost:1323/abstractWorkflows/materialize/'+id+'/', {
      type: 'GET',
      success: function(data, textStatus, jqXHR) {
        return console.log(data);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log(jqXHR);
        return alert(jqXHR.responseText);
      }
    });

    $.ajax('http://localhost:1323/abstractWorkflows/execute/'+id, {
      type: 'GET',
      success: function(data, textStatus, jqXHR) {
        return console.log(data);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log(jqXHR);
        return alert(jqXHR.responseText);
      }
    });
    
    // TODO: turn on single workflow optimization
    //return $.ajax('/php/index.php', {
    //  data: {
    //    action: 'execute',
    //    workflow: {
    //      'name': workflow.name,
    //      'nodes': workflow.nodes,
    //      'edges': workflow.edges,
    //      'tasks': workflow.tasks,
    //      'taskLinks': workflow.taskLinks || []
    //    }
    //  },
    //  type: 'POST',
    //  success: function(data, textStatus, jqXHR) {
    //    return console.log(data);
    //  },
    //  error: function(jqXHR, textStatus, errorThrown) {
    //    console.log(jqXHR);
    //    return alert(jqXHR.responseText);
    //  }
    //});
  });
  $('#dashboard').click(function() {
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
  return $('#tabs').on({
    click: function() {
      var itab;
      $('#tabs ul li').removeClass('active');
      $(this).parent('li').addClass('active');
      itab = $(this).parent('li').index();
      return openWorkflow(tabContent[itab]['wl']);
    }
  }, 'ul > li > a');
});

showChart = function(dpoints) {
  var chart;
  chart = new CanvasJS.Chart('chartContainer', {
    theme: "theme2",
    title: {
      text: "mp_bar"
    },
    animationEnabled: false,
    data: [
      {
        type: "column",
        dataPoints: dpoints
      }
    ]
  });
  return chart.render();
};

graph = new wGraph('#wlBoard');

tgraph = new wGraph('#tasksBoard');
