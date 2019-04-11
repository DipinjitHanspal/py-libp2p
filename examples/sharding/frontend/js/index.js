// import _ from 'lodash';

import {graph, blocks} from './data.js';

console.log('hello');

console.log(graph);

var nodes = graph.nodes;
var links = graph.links;


const plotBlocks = function(blocks) {
	blocks.forEach((block) => {
		var start = nodesDict[block.source]
		var end = nodesDict[block.target]
		var block = createBlock(start.x_axis, start.y_axis);
		var dx = end.x_axis - start.x_axis
			var dy = end.y_axis -  start.y_axis
			block.transition()
			.attr("transform", "translate(" + dx + "," + dy + ")")
			.duration(2000)
			.on("end", function(d){this.remove()});
	})
	return;
}

var nodesDict = {}
	nodes.forEach((node) => {
		nodesDict[node.id] = {
			"x_axis": node.x_axis,
			"y_axis": node.y_axis
		}
	})

	const linkFormatter = (link) => {
		link["x1"] = nodesDict[link.source].x_axis
		link["y1"] = nodesDict[link.source].y_axis
		link["x2"] = nodesDict[link.target].x_axis
		link["y2"] = nodesDict[link.target].y_axis
		return link
	}

	const formattedLinks = _.map(links, linkFormatter)

	var svgPaths = []
	formattedLinks.forEach((link) => {
		svgPaths.push([{
			"x": link.x1,
			"y": link.y1
		},
		{
			"x": link.x2,
			"y": link.y2
		}])
	})
	// console.log(nodesDict)
	// console.log(formattedLinks)
	console.log(svgPaths)

	const color = ["#3366cc", "#dc3912", "#ff9900", "#109618", "#990099"]

	const svgContainer = d3.select(".d3-container").append("svg")
		.attr("width", 500)
		.attr("height", 500);

	// const lines = svgContainer.selectAll("line")
	//   .attr("class", "line")
	//   .data(formattedLinks)
	//   .enter()
	//   .append("line")
	//   .style("stroke", "#999")
	//   .style("stroke-opacity", "0.6")
	//   .attr("x1", (d) => d.x1)
	//   .attr("y1", (d) => d.y1)
	//   .attr("x2", (d) => d.x2)
	//   .attr("y2", (d) => d.y2)

	// const block = svgContainer.append("path")
	// 	.attr("class", "block")
	// 	.attr("d", "M0 0h24v24H0z")
	// 	.attr("d", "M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V8l8 5 8-5v10zm-8-7L4 6h16l-8 5z")
	// 	.attr("height", 20)
	// 	.attr("width",  20);
	
	// const block = svgContainer.append('text')
	// 	.attr("class", "fa")
	// 	.attr('font-size', "10px")
	// 	.text("\uf0e0");   

	var line = d3.line()
		.x((d) => d.x)
		.y((d) => d.y)

	// var svgline = []
	var test = ""
	svgPaths.forEach((path) => {
		test += line(path)
	})
	

	var paths = svgContainer.append('path')
		.attr('d', test)
		.style("fill", "none")
		.style("stroke", "#999");

	const circles = svgContainer.selectAll("circle")
		.attr("class", "circle")
		.data(nodes)
		.enter()
		.append("circle")
		.attr("cx", (d) => d.x_axis)
		.attr("cy", (d) => d.y_axis)
		.attr("r", 5)
		.style("fill", (d) => color[d.group])

	const labels = svgContainer.selectAll("text")
		.data(nodes)
		.enter()
		.append("text")
		.attr("x", function(d) { return d.x_axis + 7; })
		.attr("y", function(d) { return d.y_axis + 2; })
		.text((d) => d.id)
		.attr("font-family", "sans-serif")
		.attr("font-size", "10px")
		.attr("fill", "black");

	const createBlock = function(x, y) {
		const block = svgContainer.append('text')
			.attr("class", "fa")
			.attr('font-size', "10px")
			.attr("x", x)
			.attr("y", y)
			.text("\uf0e0");   
		return block;
	}
	// const transition = function(paths) {
	// 	console.log("paths");
	// 	console.log(paths);
	// 	console.log(formattedLinks)
	// 	var block = createBlock();
	// 	svgPaths.forEach((path) => {
	// 		console.log("path:")
	// 		console.log(path)
	// 		var block = createBlock(path[0].x, path[0].y);
	// 		var dx = path[1].x -  path[0].x
	// 		var dy = path[1].y -  path[0].y
	// 		console.log("translate(" + dx + "," + dy + ")")
	// 		block.transition()
	// 		.attr("transform", "translate(" + dx + "," + dy + ")")
	// 		.duration(2000)
	// 		.on("end", function(d){this.remove()});
	// 	})
	// }

	// transition(paths);
	setInterval(function() {
		plotBlocks(blocks);
	}, 1000);
