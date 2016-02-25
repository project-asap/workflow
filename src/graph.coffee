wGraph = (el) ->

  # Node sizes
  rectW = 70
  rectH = 40

  # Add and remove elements on the graph object
  @addNode = (node) ->
    node.x = parseFloat(node.x)
    node.y = parseFloat(node.y)
    node.px = parseFloat(node.px)
    node.py = parseFloat(node.py)
    nodes.push node
    update()
    return

  @removeNode = (id) ->
    i = 0
    n = findNode(id)
    while i < links.length
      if links[i]['source'] == n or links[i]['target'] == n
        links.splice i, 1
      else
        i++
    index = findNodeIndex(id)
    if index != undefined
      nodes.splice index, 1
      update()
    return

  @addLink = (link) ->
    sourceNode = findNode(parseInt(link.sourceId))
    targetNode = findNode(parseInt(link.targetId))
    if sourceNode != undefined and targetNode != undefined
      link.source = sourceNode
      link.target = targetNode
      links.push link
      update()
    return

  findNode = (id) ->
    i = 0
    while i < nodes.length
      if parseInt(nodes[i].id) == id
        return nodes[i]
      i++
    return

  findNodeIndex = (id) ->
    i = 0
    while i < nodes.length
      if parseInt(nodes[i].id) == id
        return i
      i++
    return

  # set up the D3 visualisation in the specified element
  w = $(el).innerWidth()
  h = $(el).innerHeight()
  vis = @vis = d3.select(el).append('svg:svg').attr('width', w).attr('height', h)
  force = d3.layout.force().gravity(.05).distance(90).charge(-300).size([w, h])
  nodes = @nodes = force.nodes()
  links = @links = force.links()

  @clean = ->
    vis.selectAll('svg > *').remove()
    nodes.splice(0, nodes.length)
    links.splice(0, links.length)
    vis.append('defs').append('marker')
    .attr('id', 'arrow')
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 10)
    .attr('refY', 0)
    .attr('markerWidth', 5)
    .attr('markerHeight', 5)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M0,-5L10,0L0,5')

  update = ->
    force.drag()
    .on 'dragstart', (d, i) ->
      force.stop()
      return
    .on 'drag', (d, i) ->
      d.px = parseFloat(d.px)+parseFloat(d3.event.dx)
      d.py = parseFloat(d.py)+parseFloat(d3.event.dy)
      d.x = parseFloat(d.x)+parseFloat(d3.event.dx)
      d.y = parseFloat(d.y)+parseFloat(d3.event.dy)
      force.tick()
      return
    .on 'dragend', (d, i) ->
      d.fixed = true
      force.tick()
      force.resume()
      return

    link = vis.selectAll('line.link').data links, (d) ->
      d.source.id + '-' + d.target.id
    link.enter().insert('line').attr('marker-end', 'url(#arrow)')
    .attr('class', (d) ->
      if !d.cl
        'link' + d.id + ' link'
      else
        'link' + d.id + ' link ' + d.cl)
    .attr('onclick', (d) ->
      if !!d.analysis
        'selectLink(' + d.id + ')'
    )
    link.exit().remove()

    node = vis.selectAll('g.node').data(nodes, (d) -> d.id)
    nodeEnter = node.enter().append('g')
    .attr('class', (d) ->
      if !d.class
        'node' + d.id + ' node rect'
      else
        'node' + d.id + ' node ' + d.class)
    .attr('onclick', (d) ->
      if !d.operator
        'selectNode(' + d.id + ')'
      else
        'selectNode(' + d.id + ',\'task\')'
    )
    .call(force.drag)
    nodeEnter.append('rect').attr('class', 'rect')
    .attr('width', rectW).attr('height', rectH)
    .attr('x', -rectW / 2).attr('y', -rectH / 2)

    nodeEnter.append('ellipse').attr('class', 'ellipse').attr('cx', 0).attr('cy', 0)
    .attr('rx', (d) ->
      if (d.type == 'circle')
        rectH / 2
      else
        rectW / 2 - 5)
    .attr('ry', (d) ->
      if (d.type == 'circle')
        rectH / 2
      else
        rectH / 2 - 2)
    nodeEnter.append('text').attr('class', 'nodetext')
    .attr('x', 0).attr('y', 4).attr('text-anchor', 'middle')
    .text((d) -> d.name)
    node.exit().remove()

    force.on 'tick', ->
      link.attr('x1', (d) ->
        x1 = parseFloat(d.source.x)
        x2 = parseFloat(d.target.x)
        y1 = parseFloat(d.source.y)
        y2 = parseFloat(d.target.y)
        k = rectW / rectH
        if Math.abs(x1 - x2) >= Math.abs(y1 - y2) * k
          x1 - Math.sign(x1 - x2) * rectW / 2
        else
          x1 - rectH / 2 / Math.abs(y1 - y2) * (x1 - x2)
      ).attr('y1', (d) ->
        x1 = parseFloat(d.source.x)
        x2 = parseFloat(d.target.x)
        y1 = parseFloat(d.source.y)
        y2 = parseFloat(d.target.y)
        k = rectW / rectH
        if Math.abs(x1 - x2) <= Math.abs(y1 - y2) * k
          y1 - Math.sign(y1 - y2) * rectH / 2
        else
          y1 - rectW / 2 / Math.abs(x1 - x2) * (y1 - y2)
      ).attr('x2', (d) ->
        x1 = parseFloat(d.source.x)
        x2 = parseFloat(d.target.x)
        y1 = parseFloat(d.source.y)
        y2 = parseFloat(d.target.y)
        k = rectW / rectH
        if Math.abs(x1 - x2) >= Math.abs(y1 - y2) * k
          x2 + Math.sign(x1 - x2) * rectW / 2
        else
          x2 + rectH / 2 / Math.abs(y1 - y2) * (x1 - x2)
      ).attr('y2', (d) ->
        x1 = parseFloat(d.source.x)
        x2 = parseFloat(d.target.x)
        y1 = parseFloat(d.source.y)
        y2 = parseFloat(d.target.y)
        k = rectW / rectH
        if Math.abs(x1 - x2) <= Math.abs(y1 - y2) * k
          y2 + Math.sign(y1 - y2) * rectH / 2
        else
          y2 + rectW / 2 / Math.abs(x1 - x2) * (y1 - y2)
      )
      node.attr 'transform', (d) ->
        'translate(' + parseFloat(d.x) + ',' + parseFloat(d.y) + ')'
      return

    # Restart the force layout.
    force.start()
    return

  # Make it all go
  update()
  return