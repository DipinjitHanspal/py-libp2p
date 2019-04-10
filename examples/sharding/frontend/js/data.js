const nodes = [
    {"id": "aspyn", "group": 1, "x_axis": 330, "y_axis": 30},
    {"id": "alex", "group": 1, "x_axis": 380, "y_axis": 90},
    {"id": "rob", "group": 1, "x_axis": 320, "y_axis": 80},
    {"id": "zx", "group": 1, "x_axis": 360, "y_axis": 40},
    {"id": "ken", "group": 2, "x_axis": 300, "y_axis": 300},
    {"id": "jake", "group": 2, "x_axis": 350, "y_axis": 280},
    {"id": "yung", "group": 2, "x_axis": 270, "y_axis": 250},
    {"id": "ani", "group": 3, "x_axis": 140, "y_axis": 130},
    {"id": "boon", "group": 3, "x_axis": 120, "y_axis": 160},
    {"id": "evan", "group": 3, "x_axis": 160, "y_axis": 150}
]

const links = [
    {"source": "aspyn", "target": "rob"},
    {"source": "aspyn", "target": "zx"},
    {"source": "aspyn", "target": "alex"},
    {"source": "zx", "target": "alex"},
    {"source": "zx", "target": "rob"},
    {"source": "rob", "target": "alex"},
    {"source": "zx", "target": "ken"},
    {"source": "zx", "target": "yung"},
    {"source": "ken", "target": "jake"},
    {"source": "ken", "target": "yung"},
    {"source": "jake", "target": "yung"},
    {"source": "boon", "target": "ani"},
    {"source": "rob", "target": "ani"},
    {"source": "alex", "target": "ken"},
    {"source": "boon", "target": "rob"}
]

var graph = {'nodes': nodes,
         'links': links}

export {graph}