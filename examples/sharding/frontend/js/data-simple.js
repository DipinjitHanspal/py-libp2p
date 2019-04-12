// "topology": {
//         "sender": ["0"],
//         "0": ["1"],
//         "1": ["2"],
//         "2": ["3"],
//         "3": ["4"],
//         "4": ["5"],
//         "5": ["6"],
//         "6": ["7"],
//         "7": ["8"]
//     },
//     "topic_map": {
//         "0": "topic1",
//         "1": "topic1",
//         "2": "topic1",
//         "3": "topic1",
//         "4": "topic1",
//         "5": "topic1",
//         "6": "topic1",
//         "7": "topic1",
//         "8": "topic1"
//     }



const nodes = [
    {"id": "peer-sender", "group": 0, "x_axis": 40, "y_axis": 20},
    {"id": "peer-0", "group": 1, "x_axis": 120, "y_axis": 20},
    {"id": "peer-1", "group": 2, "x_axis": 220, "y_axis": 20},
    {"id": "peer-2", "group": 3, "x_axis": 40, "y_axis": 110},
    {"id": "peer-3", "group": 4, "x_axis": 120, "y_axis": 110},
    {"id": "peer-4", "group": 5, "x_axis": 220, "y_axis": 110},
    {"id": "peer-5", "group": 6, "x_axis": 40, "y_axis": 200},
    {"id": "peer-6", "group": 7, "x_axis": 120, "y_axis": 200},
    {"id": "peer-7", "group": 8, "x_axis": 220, "y_axis": 200},
]

const links = [
    {"source": "peer-sender", "target": "peer-0"},
    {"source": "peer-0", "target": "peer-1"},
    {"source": "peer-1", "target": "peer-2"},
    {"source": "peer-2", "target": "peer-3"},
    {"source": "peer-3", "target": "peer-4"},
    {"source": "peer-4", "target": "peer-5"},
    {"source": "peer-5", "target": "peer-6"},
    {"source": "peer-6", "target": "peer-7"},

]

const blocks = [
    {"source": "peer-sender", "target": "peer-0"},
    {"source": "peer-0", "target": "peer-3"},
    {"source": "peer-sender", "target": "peer-1"},
    {"source": "peer-1", "target": "peer-4"},
    {"source": "peer-1", "target": "peer-7"},
    {"source": "peer-4", "target": "peer-7"},
    {"source": "peer-2", "target": "peer-8"},
    {"source": "peer-2", "target": "peer-5"},
    {"source": "peer-0", "target": "peer-6"},
    {"source": "peer-3", "target": "peer-6"},
    {"source": "peer-sender", "target": "peer-2"},
    {"source": "peer-2", "target": "peer-5"}
]

var graph = {'nodes': nodes,
         'links': links}

export {graph, blocks}