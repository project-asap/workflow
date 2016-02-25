var wGraph;

wGraph = function(el) {
  var findNode, findNodeIndex, force, h, links, nodes, rectH, rectW, update, vis, w;
  rectW = 70;
  rectH = 40;
  this.addNode = function(node) {
    node.x = parseFloat(node.x);
    node.y = parseFloat(node.y);
    node.px = parseFloat(node.px);
    node.py = parseFloat(node.py);
    nodes.push(node);
    update();
  };
  this.removeNode = function(id) {
    var i, index, n;
    i = 0;
    n = findNode(id);
    while (i < links.length) {
      if (links[i]['source'] === n || links[i]['target'] === n) {
        links.splice(i, 1);
      } else {
        i++;
      }
    }
    index = findNodeIndex(id);
    if (index !== void 0) {
      nodes.splice(index, 1);
      update();
    }
  };
  this.addLink = function(link) {
    var sourceNode, targetNode;
    sourceNode = findNode(parseInt(link.sourceId));
    targetNode = findNode(parseInt(link.targetId));
    if (sourceNode !== void 0 && targetNode !== void 0) {
      link.source = sourceNode;
      link.target = targetNode;
      links.push(link);
      update();
    }
  };
  findNode = function(id) {
    var i;
    i = 0;
    while (i < nodes.length) {
      if (parseInt(nodes[i].id) === id) {
        return nodes[i];
      }
      i++;
    }
  };
  findNodeIndex = function(id) {
    var i;
    i = 0;
    while (i < nodes.length) {
      if (parseInt(nodes[i].id) === id) {
        return i;
      }
      i++;
    }
  };
  w = $(el).innerWidth();
  h = $(el).innerHeight();
  vis = this.vis = d3.select(el).append('svg:svg').attr('width', w).attr('height', h);
  force = d3.layout.force().gravity(.05).distance(90).charge(-300).size([w, h]);
  nodes = this.nodes = force.nodes();
  links = this.links = force.links();
  this.clean = function() {
    vis.selectAll('svg > *').remove();
    nodes.splice(0, nodes.length);
    links.splice(0, links.length);
    return vis.append('defs').append('marker').attr('id', 'arrow').attr('viewBox', '0 -5 10 10').attr('refX', 10).attr('refY', 0).attr('markerWidth', 5).attr('markerHeight', 5).attr('orient', 'auto').append('path').attr('d', 'M0,-5L10,0L0,5');
  };
  update = function() {
    var link, node, nodeEnter;
    force.drag().on('dragstart', function(d, i) {
      force.stop();
    }).on('drag', function(d, i) {
      d.px = parseFloat(d.px) + parseFloat(d3.event.dx);
      d.py = parseFloat(d.py) + parseFloat(d3.event.dy);
      d.x = parseFloat(d.x) + parseFloat(d3.event.dx);
      d.y = parseFloat(d.y) + parseFloat(d3.event.dy);
      force.tick();
    }).on('dragend', function(d, i) {
      d.fixed = true;
      force.tick();
      force.resume();
    });
    link = vis.selectAll('line.link').data(links, function(d) {
      return d.source.id + '-' + d.target.id;
    });
    link.enter().insert('line').attr('marker-end', 'url(#arrow)').attr('class', function(d) {
      if (!d.cl) {
        return 'link' + d.id + ' link';
      } else {
        return 'link' + d.id + ' link ' + d.cl;
      }
    }).attr('onclick', function(d) {
      if (!!d.analysis) {
        return 'selectLink(' + d.id + ')';
      }
    });
    link.exit().remove();
    node = vis.selectAll('g.node').data(nodes, function(d) {
      return d.id;
    });
    nodeEnter = node.enter().append('g').attr('class', function(d) {
      if (!d["class"]) {
        return 'node' + d.id + ' node rect';
      } else {
        return 'node' + d.id + ' node ' + d["class"];
      }
    }).attr('onclick', function(d) {
      if (!d.operator) {
        return 'selectNode(' + d.id + ')';
      } else {
        return 'selectNode(' + d.id + ',\'task\')';
      }
    }).call(force.drag);
    nodeEnter.append('rect').attr('class', 'rect').attr('width', rectW).attr('height', rectH).attr('x', -rectW / 2).attr('y', -rectH / 2);
    nodeEnter.append('ellipse').attr('class', 'ellipse').attr('cx', 0).attr('cy', 0).attr('rx', function(d) {
      if (d.type === 'circle') {
        return rectH / 2;
      } else {
        return rectW / 2 - 5;
      }
    }).attr('ry', function(d) {
      if (d.type === 'circle') {
        return rectH / 2;
      } else {
        return rectH / 2 - 2;
      }
    });
    nodeEnter.append('text').attr('class', 'nodetext').attr('x', 0).attr('y', 4).attr('text-anchor', 'middle').text(function(d) {
      return d.name;
    });
    node.exit().remove();
    force.on('tick', function() {
      link.attr('x1', function(d) {
        var k, x1, x2, y1, y2;
        x1 = parseFloat(d.source.x);
        x2 = parseFloat(d.target.x);
        y1 = parseFloat(d.source.y);
        y2 = parseFloat(d.target.y);
        k = rectW / rectH;
        if (Math.abs(x1 - x2) >= Math.abs(y1 - y2) * k) {
          return x1 - Math.sign(x1 - x2) * rectW / 2;
        } else {
          return x1 - rectH / 2 / Math.abs(y1 - y2) * (x1 - x2);
        }
      }).attr('y1', function(d) {
        var k, x1, x2, y1, y2;
        x1 = parseFloat(d.source.x);
        x2 = parseFloat(d.target.x);
        y1 = parseFloat(d.source.y);
        y2 = parseFloat(d.target.y);
        k = rectW / rectH;
        if (Math.abs(x1 - x2) <= Math.abs(y1 - y2) * k) {
          return y1 - Math.sign(y1 - y2) * rectH / 2;
        } else {
          return y1 - rectW / 2 / Math.abs(x1 - x2) * (y1 - y2);
        }
      }).attr('x2', function(d) {
        var k, x1, x2, y1, y2;
        x1 = parseFloat(d.source.x);
        x2 = parseFloat(d.target.x);
        y1 = parseFloat(d.source.y);
        y2 = parseFloat(d.target.y);
        k = rectW / rectH;
        if (Math.abs(x1 - x2) >= Math.abs(y1 - y2) * k) {
          return x2 + Math.sign(x1 - x2) * rectW / 2;
        } else {
          return x2 + rectH / 2 / Math.abs(y1 - y2) * (x1 - x2);
        }
      }).attr('y2', function(d) {
        var k, x1, x2, y1, y2;
        x1 = parseFloat(d.source.x);
        x2 = parseFloat(d.target.x);
        y1 = parseFloat(d.source.y);
        y2 = parseFloat(d.target.y);
        k = rectW / rectH;
        if (Math.abs(x1 - x2) <= Math.abs(y1 - y2) * k) {
          return y2 + Math.sign(y1 - y2) * rectH / 2;
        } else {
          return y2 + rectW / 2 / Math.abs(x1 - x2) * (y1 - y2);
        }
      });
      node.attr('transform', function(d) {
        return 'translate(' + parseFloat(d.x) + ',' + parseFloat(d.y) + ')';
      });
    });
    force.start();
  };
  update();
};
