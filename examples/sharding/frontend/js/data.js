const nodes = [
    {"id": "peer-sender", "group": 0, "x_axis": 280, "y_axis": 150},
    {"id": "peer-0", "group": 1, "x_axis": 380, "y_axis": 90},
    {"id": "peer-3", "group": 1, "x_axis": 320, "y_axis": 80},
    {"id": "peer-6", "group": 1, "x_axis": 360, "y_axis": 40},
    {"id": "peer-1", "group": 2, "x_axis": 300, "y_axis": 300},
    {"id": "peer-4", "group": 2, "x_axis": 350, "y_axis": 280},
    {"id": "peer-7", "group": 2, "x_axis": 270, "y_axis": 250},
    {"id": "peer-2", "group": 3, "x_axis": 140, "y_axis": 130},
    {"id": "peer-5", "group": 3, "x_axis": 120, "y_axis": 160},
    {"id": "peer-8", "group": 3, "x_axis": 160, "y_axis": 150}
]

const links = [
    {"source": "peer-sender", "target": "peer-0"},
    {"source": "peer-sender", "target": "peer-1"},
    {"source": "peer-sender", "target": "peer-2"},
    {"source": "peer-0", "target": "peer-3"},
    {"source": "peer-3", "target": "peer-6"},
    {"source": "peer-6", "target": "peer-0"},
    {"source": "peer-1", "target": "peer-4"},
    {"source": "peer-2", "target": "peer-5"},
    {"source": "peer-8", "target": "peer-2"},
    {"source": "peer-5", "target": "peer-8"},
    {"source": "peer-4", "target": "peer-7"},
    {"source": "peer-1", "target": "peer-7"}
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