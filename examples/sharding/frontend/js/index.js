// import _ from 'lodash';

import {graph, blocks} from './data.js';
import {EasySQS} from './EasySQS.js'
import {config} from './config.js'

console.log('starting up...');

var nodes = graph.nodes;
var links = graph.links;

var queue = "https://sqs.us-east-1.amazonaws.com/875814277611/test-queue";

var sqs = new EasySQS(config);


var str = "{\"type": \"send\", \"sender\": \"peer-sender\", \"receiver\": \"b'peer-5'\"}"

var throughput = [].push(0);
// var throughput = 0;

var blockSize = 10;
var messageCounts = {}
nodes.forEach((node1) => {
	nodes.forEach((node2) => {
		// console.log(node1.id + "," + node2.id)
		messageCounts[node1.id + "," + node2.id] = 0;
	});
});

const pullData = function() {
	var messages = []
	sqs.receive(queue).then((packet) => {
		// console.log("packet")
		console.log(packet)
		packet.Messages.forEach((rawMessage) => {
			var text = rawMessage.Body.replace("b'", "****");
			text = text.replace("****", "");
			text = text.replace("'", "");
			console.log(text)
			var message = JSON.parse(text);
			if (message.type === "send") {
				messages.push(message); 
			} else if (message.type === "ack") {
				console.log(message)
				throughput[0] += 10;
			}
			// call delete message from queue using easySQS
			sqs.delete(rawMessage.ReceiptHandle, queue);
		});
	}).then(() => {
		var blocks = convertMessages(messages);
		plotBlocks(blocks);
	})

}

const convertMessages = function(messages) {
	var blocks = [];
	// console.log("in convert")
	messages.forEach((message) => {
		// console.log(message)
		var key = "" + message.sender + ","  + message.receiver
		if (!(key in messageCounts)) {
			console.log(key + "sender or receiver does not exist");
		} else if (messageCounts[key] + 1 >= blockSize) {
			// should display block
			var block = {"source": message.sender, "target": message.receiver}
			blocks.push(block)
			messageCounts[key] = 0;
		} else {
			// console.log("updating count " + key)
			// console.log("old: " + messageCounts[key])
			messageCounts[key] = messageCounts[key] + 1;
			// console.log("new: " + messageCounts[key])
		}
	});
	if (blocks.length > 0) {
		console.log("blocks length: " + blocks.length)
	}
	return blocks;
}


const plotBlocks = function(blocks) {
	blocks.forEach((block) => {
		// console.log("blocks");
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

	const throughputCounter = svgContainer.select("p")
		.data(throughput)
		.enter()
		.append("p")
		.text((d) => "hello world " + d)

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

	// // transition(paths);
	// setInterval(function() {
	// 	plotBlocks(blocks);
	// }, 1000);


// pullData();

// setInterval(function() {
// 	pullData();
// }, 3000);
