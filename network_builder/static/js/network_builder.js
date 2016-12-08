

var nodes,
    edges,
    network;
var num_nodes = 0;
var num_edges = 0;
var selected_nodes = [];
var last_edge = undefined;
// convenience method to stringify a JSON object
function toJSON(obj) {
	return JSON.stringify(obj, null, 4);
}

function network_load() {
	document.getElementById('loadnw').innerHTML = '<img src="' + DIR + 'loading.gif" />';
	var opt = document.getElementById("network_choice").options;
	var name = opt[opt.selectedIndex].text;
	$.post(LOAD_NETWORK_URL, {
		'name' : name
	}).done(function(data) {
		try {
			var obj = JSON.parse(data);
			network_reset();
			var last_node = 0;
			var last_edge = 0;
			for (var x = 0; x < obj.nodes.length; x++) {
				nodes.add(obj.nodes[x]);
				if (last_node < obj.nodes[x].id)
					last_node = obj.nodes[x].id;

			}
			for (var x = 0; x < obj.edges.length; x++) {
				edges.add(obj.edges[x]);
				if (last_edge < obj.edges[x].id)
					last_edge = obj.edges[x].id;
			}
			num_nodes = last_node;
			num_edges = last_edge;
			document.getElementById('network_name').value = name;
		} catch(err) {
			alert(err.message);
			return 0;
		}

		document.getElementById('loadnw').innerHTML = '';
	});
}

function network_reset() {
	var delnodes = nodes.get();
	var deledges = edges.get();
	for (var x = 0; x < delnodes.length; x++) {
		nodes.remove({
			id : delnodes[x].id
		});
	}
	for (var x = 0; x < deledges.length; x++) {
		edges.remove({
			id : deledges[x].id
		});
	}
}

function network_save() {

	document.getElementById('load').innerHTML = '<img src="' + DIR + 'loading.gif" />';

	var nname = document.getElementById('network_name').value;
	if (nname != "") {
		var obj = {
			'nodes' : nodes.get(),
			'edges' : edges.get()
		};
		params = {
			'name' : nname,
			'network' : toJSON(obj)
		};
		$.post(SAVE_URL, params).done(function(data) {
			document.getElementById('load').innerHTML = '';
		});
	} else {
		alert("Network without name is not valid");
	}

}

function network_run() {

	document.getElementById('runnw').innerHTML = '<img src="' + DIR + 'loading.gif" />';

	var nname = document.getElementById('network_name').value;
	if (nname != "") {
		var obj = {
			'nodes' : nodes.get(),
			'edges' : edges.get()
		};
		params = {
			'name' : nname,
			'network' : toJSON(obj)
		};
		$.post(RUN_URL, params).done(function(data) {
			document.getElementById('runnw').innerHTML = '';
		});
	} else {
		alert("Network without name is not valid");
	}

}


function addNode(element) {
	try {
		nodes.add({
			id : ++num_nodes,
			type : element,
			image : DIR + element + '.png',
			shape : 'image'
		});
	} catch (err) {
		alert(err);
	}
}

function removeNode() {
	if (selected_nodes.length > 0) {
		try {
			nodes.remove({
				id : selected_nodes[0]
			});
		} catch (err) {
			alert(err);
		}
	}
}

function addEdge(from, to) {
	try {
		edges.add({
			id : ++num_edges,
			from : from,
			to : to
		});
	} catch (err) {
		alert(err);
	}
}

function removeEdge() {
	if (last_edge != undefined) {
		try {
			edges.remove({
				id : last_edge
			});
		} catch (err) {
			alert(err);
		}
	}
}

function node_click_action(params) {
	var nodes = params["nodes"];
	if (nodes.length > 0) {
		selected_nodes.push(nodes[0]);
	} else {
		selected_nodes = [];
	}
	if (selected_nodes.length == 2) {
		if (selected_nodes[0].id == selected_nodes[1].id) {
			selected_nodes.pop();
		} else {
			addEdge(selected_nodes[0], selected_nodes[1]);
			selected_nodes = [];
		}
	}
	var edge = params['edges'];
	if (edge.length > 0) {
		last_edge = edge[0];
	} else {
		last_edge = undefined;
	}
}

function node_doubleclick_action(params) {
	var nodesid = params["nodes"];
	var edgesid = params["edges"];
	var href = undefined;
	var wname = undefined;
	if (nodesid.length > 0) {
		var node = nodes.get().find(function(v) {
			return v.id == nodesid[0];
		});
		wname = "nodes__" + nodesid[0];
		if (node.djvalue == undefined) {
			href = ADMIN_URLS[node.type + "_add"];
		} else {
			href = ADMIN_URLS[node.type + "_change"].replace("/0/", "/" + node.djvalue + "/");
		}
	} else {
		if (edgesid.length > 0) {
			var edge = edges.get().find(function(v) {
				return v.id == edgesid[0];
			});
			wname = "edges__" + edgesid[0];
			if (edge.djvalue == undefined) {
				href = ADMIN_URLS['edges_add'];
			} else {
				href = ADMIN_URLS["edges_change"].replace("/0/", "/" + edge.djvalue + "/");
			}
		}
	}

	win = window.open(href, wname, 'height=500,width=800,resizable=yes,scrollbars=yes');
	win.focus();

	window.dismissChangeRelatedObjectPopup = function(window, value, obj, new_value) {
		window.close();
	};
	window.dismissAddRelatedObjectPopup = function(window, value, obj) {
		var name_list = window.name.split("__");
		var _type = name_list[0];
		var id = name_list[1];

		if (_type == 'nodes') {
			nodes.update([{
				id : parseInt(id),
				djvalue : value
			}]);
		}else{
			if(_type == 'edges'){
			edges.update([{
				id : parseInt(id),
				djvalue : value
			}]);				
			}
		}

		window.close();
	};

}

function draw() {
	// create an array with nodes
	nodes = new vis.DataSet();

	// create an array with edges
	edges = new vis.DataSet();

	// create a network
	var container = document.getElementById('network');
	var data = {
		nodes : nodes,
		edges : edges
	};
	//var options = {};

	var options = {
		interaction : {
			// navigationButtons: true,
			keyboard : true
		}
	};

	network = new vis.Network(container, data, options);
	network.on("click", node_click_action);
	network.on("doubleClick", node_doubleclick_action);
}
