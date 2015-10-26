var barHeight, barWidth, click, color, diagonal, duration, i, margin, root, svg, tree, updateMetaTree, width;

margin = {
  top: 30,
  right: 20,
  bottom: 30,
  left: 20
};

width = 320 - margin.left - margin.right;

barHeight = 20;

barWidth = width * .8;

i = 0;

duration = 400;

root = void 0;

tree = d3.layout.tree().nodeSize([0, 20]);

diagonal = d3.svg.diagonal().projection(function(d) {
  return [d.y, d.x];
});

svg = d3.select('#metadataTree').append('svg').attr('width', width + margin.left + margin.right).append('g').attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

updateMetaTree = function(source) {
  var height, link, node, nodeEnter, nodes;
  root = source;
  nodes = tree.nodes(root);
  height = Math.max(500, nodes.length * barHeight + margin.top + margin.bottom);
  d3.select('svg').transition().duration(duration).attr('height', height);
  d3.select(self.frameElement).transition().duration(duration).style('height', height + 'px');
  nodes.forEach(function(n, i) {
    n.x = i * barHeight;
  });
  node = svg.selectAll('g.node').data(nodes, function(d) {
    return d.id || (d.id = ++i);
  });
  nodeEnter = node.enter().append('g').attr('class', 'node').attr('transform', function(d) {
    return 'translate(' + source.y0 + ',' + source.x0 + ')';
  }).style('opacity', 1e-6);
  nodeEnter.append('rect').attr('y', -barHeight / 2).attr('height', barHeight).attr('width', barWidth).style('fill', color).on('click', click);
  nodeEnter.append('text').attr('dy', 3.5).attr('dx', 5.5).text(function(d) {
    return Object.keys(d)[0];
  });
  nodeEnter.transition().duration(duration).attr('transform', function(d) {
    return 'translate(' + d.y + ',' + d.x + ')';
  }).style('opacity', 1);
  node.transition().duration(duration).attr('transform', function(d) {
    return 'translate(' + d.y + ',' + d.x + ')';
  }).style('opacity', 1).select('rect').style('fill', color);
  node.exit().transition().duration(duration).attr('transform', function(d) {
    return 'translate(' + source.y + ',' + source.x + ')';
  }).style('opacity', 1e-6).remove();
  link = svg.selectAll('path.link').data(tree.links(nodes), function(d) {
    return d.target.id;
  });
  link.enter().insert('path', 'g').attr('class', 'link').attr('d', function(d) {
    var o;
    o = {
      x: source.x0,
      y: source.y0
    };
    return diagonal({
      source: o,
      target: o
    });
  }).transition().duration(duration).attr('d', diagonal);
  link.transition().duration(duration).attr('d', diagonal);
  link.exit().transition().duration(duration).attr('d', function(d) {
    var o;
    o = {
      x: source.x,
      y: source.y
    };
    return diagonal({
      source: o,
      target: o
    });
  }).remove();
  nodes.forEach(function(d) {
    d.x0 = d.x;
    d.y0 = d.y;
  });
};

click = function(d) {
  if (d.children) {
    d._children = d.children;
    d.children = null;
  } else {
    d.children = d._children;
    d._children = null;
  }
  updateMetaTree(d);
};

color = function(d) {
  if (d._children) {
    return '#3182bd';
  } else if (d.children) {
    return '#c6dbef';
  } else {
    return '#fd8d3c';
  }
};
