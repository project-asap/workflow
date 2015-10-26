margin =
  top: 30
  right: 20
  bottom: 30
  left: 20
width = 320 - (margin.left) - (margin.right)
barHeight = 20
barWidth = width * .8
i = 0
duration = 400
root = undefined
tree = d3.layout.tree().nodeSize([0,20])
diagonal = d3.svg.diagonal().projection((d) -> [d.y,d.x])
svg = d3.select('#metadataTree').append('svg').attr('width', width + margin.left + margin.right).append('g').attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')

updateMetaTree = (source) ->
  root = source
# Compute the flattened node list. TODO use d3.layout.hierarchy.
  nodes = tree.nodes(root)
  height = Math.max(500, nodes.length * barHeight + margin.top + margin.bottom)
  d3.select('svg').transition().duration(duration).attr 'height', height
  d3.select(self.frameElement).transition().duration(duration).style 'height', height + 'px'
  # Compute the "layout".
  nodes.forEach (n, i) ->
    n.x = i * barHeight
    return
  # Update the nodes…
  node = svg.selectAll('g.node').data(nodes, (d) ->
    d.id or (d.id = ++i)
  )
  nodeEnter = node.enter().append('g').attr('class', 'node').attr('transform', (d) ->
    'translate(' + source.y0 + ',' + source.x0 + ')'
  ).style('opacity', 1e-6)
  # Enter any new nodes at the parent's previous position.
  nodeEnter.append('rect').attr('y', -barHeight / 2).attr('height', barHeight).attr('width', barWidth).style('fill', color).on 'click', click
  nodeEnter.append('text').attr('dy', 3.5).attr('dx', 5.5).text (d) ->
    Object.keys(d)[0]
  # Transition nodes to their new position.
  nodeEnter.transition().duration(duration).attr('transform', (d) ->
    'translate(' + d.y + ',' + d.x + ')'
  ).style 'opacity', 1
  node.transition().duration(duration).attr('transform', (d) ->
    'translate(' + d.y + ',' + d.x + ')'
  ).style('opacity', 1).select('rect').style 'fill', color
  # Transition exiting nodes to the parent's new position.
  node.exit().transition().duration(duration).attr('transform', (d) ->
    'translate(' + source.y + ',' + source.x + ')'
  ).style('opacity', 1e-6).remove()
  # Update the links…
  link = svg.selectAll('path.link').data(tree.links(nodes), (d) ->
    d.target.id
  )
  # Enter any new links at the parent's previous position.
  link.enter().insert('path', 'g').attr('class', 'link').attr('d', (d) ->
    o =
      x: source.x0
      y: source.y0
    diagonal
      source: o
      target: o
  ).transition().duration(duration).attr 'd', diagonal
  # Transition links to their new position.
  link.transition().duration(duration).attr 'd', diagonal
  # Transition exiting nodes to the parent's new position.
  link.exit().transition().duration(duration).attr('d', (d) ->
    o =
      x: source.x
      y: source.y
    diagonal
      source: o
      target: o
  ).remove()
  # Stash the old positions for transition.
  nodes.forEach (d) ->
    d.x0 = d.x
    d.y0 = d.y
    return
  return

# Toggle children on click.

click = (d) ->
  if d.children
    d._children = d.children
    d.children = null
  else
    d.children = d._children
    d._children = null
  updateMetaTree(d)
  return

color = (d) ->
  if d._children then '#3182bd' else if d.children then '#c6dbef' else '#fd8d3c'
