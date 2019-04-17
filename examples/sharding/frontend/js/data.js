const nodes = [
    {"id": "peer-sender", "group": 0, "x_axis": 200, "y_axis": 150},
    {"id": "peer-0", "group": 1, "x_axis": 250, "y_axis": 90},
    {"id": "peer-2", "group": 3, "x_axis": 90, "y_axis": 120},
    {"id": "peer-3", "group": 1, "x_axis": 340, "y_axis": 80},
    {"id": "peer-6", "group": 1, "x_axis": 280, "y_axis": 40},
    {"id": "peer-1", "group": 2, "x_axis": 200, "y_axis": 240},
    {"id": "peer-4", "group": 2, "x_axis": 240, "y_axis": 280},
    {"id": "peer-7", "group": 2, "x_axis": 160, "y_axis": 320},
    {"id": "peer-5", "group": 3, "x_axis": 60, "y_axis": 60},
    {"id": "peer-8", "group": 3, "x_axis": 40, "y_axis": 190}
]

const links = [
    {"source": "peer-sender", "target": "peer-0"},
    {"source": "peer-sender", "target": "peer-1"},
    {"source": "peer-sender", "target": "peer-2"},
    {"source": "peer-0", "target": "peer-3"},
    {"source": "peer-0", "target": "peer-6"},
    {"source": "peer-1", "target": "peer-4"},
    {"source": "peer-1", "target": "peer-7"},
    {"source": "peer-2", "target": "peer-5"},
    {"source": "peer-2", "target": "peer-8"}
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