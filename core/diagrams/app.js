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

function dipgraphDiagram(){
    diagram.layout = getLayeredDigraphLayout()
}

function forceDirectedDiagram(){
    diagram.layout = getForceDirectedLayout()
}

const diagram =
  new go.Diagram("DiagramDiv",
    {
      "undoManager.isEnabled": true,
      layout: getForceDirectedLayout()
    });

function getNodeDataArray(nodeKeys) {
    let nodes = []
    let groupKeys = []
    for (let node of diagramData.nodes) {
        if (nodeKeys.includes(node.key)) {
            nodes.push(node);
            if (node.hasOwnProperty("group")) {
                groupKeys.push(node.group)
            }
        }
    }
    let groups = diagramData.nodes.filter(node => groupKeys.includes(node.key))
    return nodes.concat(groups);
}

function showImports(e, obj) {
    dipgraphDiagram()
    let linkDataArray = diagramData.links.filter(node => node.to === obj.part.data.key);
    let nodeKeys = [obj.part.data.key]
    for (let link of linkDataArray) {
        nodeKeys.push(link.from);
    }
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);

}

function showExports(e, obj) {
    dipgraphDiagram()
    let linkDataArray = diagramData.links.filter(node => node.from === obj.part.data.key);
    let nodeKeys = [obj.part.data.key]
    for (let link of linkDataArray) {
        nodeKeys.push(link.to);
    }
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);
}

function showAllDependencies(e, obj) {
    dipgraphDiagram()
    let linkDataArray = diagramData.links.filter(
        node => node.to === obj.part.data.key || node.from === obj.part.data.key
    );
    let nodeKeys = [obj.part.data.key]
    for (let link of linkDataArray) {
        if (link.from === obj.part.data.key){
            nodeKeys.push(link.to);
        } else {
            nodeKeys.push(link.from);
        }
    }
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);
}

function showGroupModules(gropu_key){
    function _showGroupModules(e, obj) {
        forceDirectedDiagram()
        let nodeDataArray = diagramData.nodes.filter(node => node.group === gropu_key || node.key === gropu_key);
        diagram.model = new go.GraphLinksModel(nodeDataArray);
    }
    return _showGroupModules
}

function showAllModules(e, obj) {
    forceDirectedDiagram()
    let nodeDataArray = diagramData.nodes;
    diagram.model = new go.GraphLinksModel(nodeDataArray);
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

diagram.nodeTemplate =
  new go.Node("Auto", { contextMenu: nodeContextMenu })
    .add(
      new go.Shape("RoundedRectangle")
        .bind("fill", "color"),
      new go.TextBlock({ margin: 5, fill: "white" })
        .bind("text", "key")
    );

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
      new go.Shape( { toArrow: "Standard" }),
      new go.TextBlock({ text: "Text Block", background: "white", margin: 2 })
        .bind("text")
    );

function getGroupContextMenu(groups){
    let menu = [
        go.GraphObject.build("ContextMenuButton", { click: showAllModules })
        .add(new go.TextBlock("All modules"))
    ];
    let defaultKeys = ["built_in", "third_party"]
    let groupKeys = []
    for (let group of groups) {
        if (!defaultKeys.includes(group.key)) {
            groupKeys.push(group.key);
        }
    }
    groupKeys.sort()
    groupKeys = defaultKeys.concat(groupKeys)
    for (let key of groupKeys) {
        menu.push(
            go.GraphObject.build("ContextMenuButton", { click: showGroupModules(key) })
                .add(new go.TextBlock(key))
        )
    }
    return menu
}

let groupsArray = diagramData.nodes.filter(node => node.isGroup)
let groupContextMenu = getGroupContextMenu(groupsArray)

diagram.contextMenu =
  go.GraphObject.build("ContextMenu")
    .add(
      ...groupContextMenu
    );


let nodeDataArray = diagramData.nodes;
diagram.model = new go.GraphLinksModel(nodeDataArray);
