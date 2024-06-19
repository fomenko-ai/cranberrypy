const colors = {
  white: '#FFFFFF',
  black: '#101920',
};

go.Shape.defineArrowheadGeometry('NullPoint', 'm 0,0 l 0,0');
go.Shape.defineArrowheadGeometry('Standard', 'F1 m 0,0 l 8,4 -8,4 2,-4 z');
go.Shape.defineArrowheadGeometry('StretchedDiamond', 'F1 m 0,3 l 5,-3 5,3 -5,3 -5,-3 z');

function readJsonFile(filePath) {
    let request = new XMLHttpRequest();
    request.open('GET', filePath, false);
    request.send(null);

    if (request.status === 200) {
        return JSON.parse(request.responseText);
    } else {
        throw new Error('Unable to load JSON file at ' + filePath);
    }
}

let diagramData = readJsonFile('./core/diagrams/data.json')

console.log(diagramData)

function textNodeTemplate(){
    diagram.nodeTemplate = new go.Node("Auto", { contextMenu: nodeContextMenu })
    .add(
      new go.Shape("RoundedRectangle")
        .bind("fill", "color"),
      new go.TextBlock({ margin: 5, fill: colors.black })
        .bind("text", "text")
    );
}

function shortInfoNodeTemplate(){
    diagram.nodeTemplate = new go.Node("Auto", { contextMenu: nodeContextMenu })
    .add(
      new go.Shape("RoundedRectangle")
        .bind("fill", "color"),
      new go.TextBlock({ margin: 5, fill: colors.black })
        .bind("text", "shortInfo")
    );
}

function getLayeredDigraphLayout(){
    return new go.LayeredDigraphLayout(
          {
              direction: 90,
              layerSpacing: 200,
              columnSpacing: 100
          }
      )
}

function getForceDirectedLayout(){
    return new go.ForceDirectedLayout()
}

function digraphDiagram(){
    diagram.layout = getLayeredDigraphLayout();
}

function forceDirectedDiagram(){
    diagram.layout = getForceDirectedLayout();
}

const diagram =
  new go.Diagram("DiagramDiv",
    {
      "undoManager.isEnabled": true,
      layout: getForceDirectedLayout()
    });

function getNodeDataArray(selectedNodeKey, nodeKeys) {
    let nodes = [];
    let groupKeys = [];
    for (let node of diagramData.nodes) {
        if (nodeKeys.includes(node.key)) {
            nodes.push(node);
            if (node.hasOwnProperty("group")) {
                groupKeys.push(node.group)
            }
        }
    }
    let groups = diagramData.nodes.filter(node => groupKeys.includes(node.key));
    nodes = nodes.concat(groups);
    nodes.forEach(node => node.key === selectedNodeKey ? node.text = node.fullInfo : node.text = node.shortInfo);
    return nodes;
}

function showImports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let linkDataArray = diagramData.links.filter(node => node.to === selectedNodeKey);
    let nodeKeys = [selectedNodeKey]
    for (let link of linkDataArray) {
        nodeKeys.push(link.from);
    }
    diagram.model = new go.GraphLinksModel(getNodeDataArray(selectedNodeKey, nodeKeys), linkDataArray);
    textNodeTemplate();
}

function showExports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let linkDataArray = diagramData.links.filter(node => node.from === selectedNodeKey);
    let nodeKeys = [selectedNodeKey]
    for (let link of linkDataArray) {
        nodeKeys.push(link.to);
    }
    diagram.model = new go.GraphLinksModel(getNodeDataArray(selectedNodeKey, nodeKeys), linkDataArray);
    textNodeTemplate();
}

function showAllDependencies(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let linkDataArray = diagramData.links.filter(
        node => node.to === selectedNodeKey || node.from === selectedNodeKey
    );
    let nodeKeys = [obj.part.data.key]
    for (let link of linkDataArray) {
        if (link.from === obj.part.data.key){
            nodeKeys.push(link.to);
        } else {
            nodeKeys.push(link.from);
        }
    }
    diagram.model = new go.GraphLinksModel(getNodeDataArray(selectedNodeKey, nodeKeys), linkDataArray);
    textNodeTemplate();
}

function showGroupModules(selectedGroupKey){
    function _showGroupModules(e, obj) {
        forceDirectedDiagram();
        let nodeDataArray = diagramData.nodes.filter(node => node.group === selectedGroupKey || node.key === selectedGroupKey);
        diagram.model = new go.GraphLinksModel(nodeDataArray);
        shortInfoNodeTemplate();
    }
    return _showGroupModules
}

function showAllModules(e, obj) {
    forceDirectedDiagram()
    let nodeDataArray = diagramData.nodes;
    diagram.model = new go.GraphLinksModel(nodeDataArray);
    shortInfoNodeTemplate()
}

const nodeContextMenu =
  go.GraphObject.build("ContextMenu")
    .add(
      go.GraphObject.build("ContextMenuButton", { click: showAllDependencies })
        .add(new go.TextBlock("Dependencies")),
      go.GraphObject.build("ContextMenuButton", { click: showImports })
        .add(new go.TextBlock("Imports")),
      go.GraphObject.build("ContextMenuButton", { click: showExports })
        .add(new go.TextBlock("Exports")),
      go.GraphObject.build("ContextMenuButton", { click: showAllModules })
        .add(new go.TextBlock("All modules"))
    );

shortInfoNodeTemplate();
diagram.linkTemplate =
  new go.Link({
      routing: go.Routing.AvoidsNodes,
      curve: go.Curve.JumpGap,
      mouseEnter: (e, link) => link.elt(0).stroke = "rgba(0,90,156,0.3)",
      mouseLeave: (e, link) => link.elt(0).stroke = "transparent"
    })
    .add(
      new go.Shape( { isPanelMain: true, stroke: "transparent", strokeWidth: 8 }),
      new go.Shape( { isPanelMain: true }),
      new go.Shape({toArrow: "NullPoint", scale: 2, stroke: colors.white, fill: colors.black}).bind("toArrow"),
      new go.Shape({fromArrow: "NullPoint", scale: 2, stroke: colors.white, fill: colors.black}).bind("fromArrow"),
      new go.TextBlock({ text: "Text Block", background: "white", margin: 2 })
        .bind("text")
    );

function getGroupContextMenu(groups){
    let menu = [
        go.GraphObject.build("ContextMenuButton", { click: showAllModules })
        .add(new go.TextBlock("All modules"))
    ];
    let defaultKeys = ["built_in", "third_party"];
    let groupKeys = [];
    for (let group of groups) {
        if (!defaultKeys.includes(group.key)) {
            groupKeys.push(group.key);
        }
    }
    groupKeys.sort();
    groupKeys = defaultKeys.concat(groupKeys);
    for (let key of groupKeys) {
        menu.push(
            go.GraphObject.build("ContextMenuButton", { click: showGroupModules(key) })
                .add(new go.TextBlock(key))
        )
    }
    return menu
}

let groupsArray = diagramData.nodes.filter(node => node.isGroup);
let groupContextMenu = getGroupContextMenu(groupsArray);

diagram.contextMenu =
  go.GraphObject.build("ContextMenu")
    .add(
      ...groupContextMenu
    );


let nodeDataArray = diagramData.nodes;
diagram.model = new go.GraphLinksModel(nodeDataArray);
