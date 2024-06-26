const colors = {
  white: '#FFFFFF',
  black: '#101920',
};

go.Shape.defineArrowheadGeometry('NullPoint', 'm 0,0 l 0,0');
go.Shape.defineArrowheadGeometry('Standard', 'F1 m 0,0 l 8,4 -8,4 2,-4 z');
go.Shape.defineArrowheadGeometry('OpenTriangle', 'm 0,0 l 8,4 -8,4');
go.Shape.defineArrowheadGeometry('Triangle', 'F1 m 0,0 l 8,4.62 -8,4.62 z');
go.Shape.defineArrowheadGeometry('BackwardTriangle', 'F1 m 8,4 l 0,4 -8,-4 8,-4 0,4 z');
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

function textNodeTemplate(menu){
    diagram.nodeTemplate = new go.Node("Auto", { contextMenu: menu })
    .add(
      new go.Shape("RoundedRectangle")
        .bind("fill", "color"),
      new go.TextBlock({ margin: 5, fill: colors.black })
        .bind("text", "text")
    );
}

function shortInfoNodeTemplate(menu){
    diagram.nodeTemplate = new go.Node("Auto", { contextMenu: menu })
    .add(
      new go.Shape("RoundedRectangle")
        .bind("fill", "color"),
      new go.TextBlock({ margin: 5, fill: colors.black })
        .bind("text", "shortInfo")
    );
}

function fullInfoNodeTemplate(menu){
    diagram.nodeTemplate = new go.Node("Auto", { contextMenu: menu })
    .add(
      new go.Shape("RoundedRectangle")
        .bind("fill", "color"),
      new go.TextBlock({ margin: 5, fill: colors.black })
        .bind("text", "fullInfo")
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
    return nodes;
}

function showModuleImports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let linkDataArray = diagramData.links.filter(node => (node.to === selectedNodeKey) && !node.isClass);
    let nodeKeys = [selectedNodeKey]
    for (let link of linkDataArray) {
        nodeKeys.push(link.from);
    }
    diagram.model = new go.GraphLinksModel(getNodeDataArray(selectedNodeKey, nodeKeys), linkDataArray);
    shortInfoNodeTemplate(nodeModuleContextMenu);
}

function showClassImports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let linkDataArray = diagramData.links.filter(node => node.to === selectedNodeKey);
    let nodeKeys = [selectedNodeKey]
    for (let link of linkDataArray) {
        nodeKeys.push(link.from);
    }
    diagram.model = new go.GraphLinksModel(getNodeDataArray(selectedNodeKey, nodeKeys), linkDataArray);
    fullInfoNodeTemplate(nodeClassContextMenu);
}

function showModuleExports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let linkDataArray = diagramData.links.filter(node => (node.from === selectedNodeKey) && !node.isClass);
    let nodeKeys = [selectedNodeKey]
    for (let link of linkDataArray) {
        nodeKeys.push(link.to);
    }
    diagram.model = new go.GraphLinksModel(getNodeDataArray(selectedNodeKey, nodeKeys), linkDataArray);
    shortInfoNodeTemplate(nodeModuleContextMenu);
}

function showClassExports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let linkDataArray = diagramData.links.filter(node => node.from === selectedNodeKey);
    let nodeKeys = [selectedNodeKey]
    for (let link of linkDataArray) {
        nodeKeys.push(link.to);
    }
    diagram.model = new go.GraphLinksModel(getNodeDataArray(selectedNodeKey, nodeKeys), linkDataArray);
    fullInfoNodeTemplate(nodeClassContextMenu);
}

function showAllModuleDependencies(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let linkDataArray = diagramData.links.filter(
        node => (node.to === selectedNodeKey || node.from === selectedNodeKey) && !node.isClass
    );
    let nodeKeys = [selectedNodeKey ];
    for (let link of linkDataArray) {
        if (link.from === selectedNodeKey){
            nodeKeys.push(link.to);
        } else {
            nodeKeys.push(link.from);
        }
    }
    diagram.model = new go.GraphLinksModel(getNodeDataArray(selectedNodeKey, nodeKeys), linkDataArray);
    textNodeTemplate(nodeModuleContextMenu);
}

function showAllClassDependencies(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let linkDataArray = diagramData.links.filter(
        node => node.to === selectedNodeKey || node.from === selectedNodeKey
    );
    let nodeKeys = [selectedNodeKey]
    for (let link of linkDataArray) {
        if (link.from === selectedNodeKey){
            nodeKeys.push(link.to);
        } else {
            nodeKeys.push(link.from);
        }
    }
    diagram.model = new go.GraphLinksModel(getNodeDataArray(selectedNodeKey, nodeKeys), linkDataArray);
    fullInfoNodeTemplate(nodeClassContextMenu);
}

function showGroupModules(selectedGroupKey){
    function _showGroupModules(e, obj) {
        forceDirectedDiagram();
        let nodeDataArray = diagramData.nodes.filter(node => (node.group === selectedGroupKey || node.key === selectedGroupKey) && !node.isClass);
        diagram.model = new go.GraphLinksModel(nodeDataArray);
        shortInfoNodeTemplate(nodeModuleContextMenu);
    }
    return _showGroupModules
}

function showModuleClasses(e, obj) {
    forceDirectedDiagram()
    let selectedNode = obj.part.data;
    let selectedNodeKey = selectedNode.key;
    let nodeDataArray = diagramData.nodes.filter(node => node.module === selectedNodeKey);
    if (nodeDataArray) {
        let nodeKeys = nodeDataArray.map(node => node.key)
        diagram.model = new go.GraphLinksModel(getNodeDataArray(selectedNodeKey, nodeKeys));
        fullInfoNodeTemplate(nodeClassContextMenu);
    } else {
        diagram.model = new go.GraphLinksModel(getNodeDataArray(selectedNodeKey, [selectedNodeKey]));
        shortInfoNodeTemplate(nodeModuleContextMenu);
    }
}

function showAllModules(e, obj) {
    forceDirectedDiagram()
    let nodeDataArray = diagramData.nodes.filter(node => !node.isClass);
    diagram.model = new go.GraphLinksModel(nodeDataArray);
    textNodeTemplate(nodeModuleContextMenu)
}

const nodeModuleContextMenu =
  go.GraphObject.build("ContextMenu")
    .add(
      go.GraphObject.build("ContextMenuButton", { click: showModuleClasses })
        .add(new go.TextBlock("Classes")),
      go.GraphObject.build("ContextMenuButton", { click: showAllModuleDependencies })
        .add(new go.TextBlock("Dependencies")),
      go.GraphObject.build("ContextMenuButton", { click: showModuleImports })
        .add(new go.TextBlock("Imports")),
      go.GraphObject.build("ContextMenuButton", { click: showModuleExports })
        .add(new go.TextBlock("Exports")),
      go.GraphObject.build("ContextMenuButton", { click: showAllModules })
        .add(new go.TextBlock("All modules"))
    );

const nodeClassContextMenu =
  go.GraphObject.build("ContextMenu")
    .add(
      go.GraphObject.build("ContextMenuButton", { click: showAllClassDependencies })
        .add(new go.TextBlock("Dependencies")),
      go.GraphObject.build("ContextMenuButton", { click: showClassImports })
        .add(new go.TextBlock("Imports")),
      go.GraphObject.build("ContextMenuButton", { click: showClassExports })
        .add(new go.TextBlock("Exports")),
      go.GraphObject.build("ContextMenuButton", { click: showAllModules })
        .add(new go.TextBlock("All modules"))
    );

textNodeTemplate(nodeModuleContextMenu);
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
      new go.Shape({toArrow: "NullPoint", scale: 2, stroke: colors.black, fill: colors.black}).bind("toArrow"),
      new go.Shape({fromArrow: "NullPoint", scale: 2, stroke: colors.black, fill: colors.white}).bind("fromArrow"),
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


let nodeDataArray = diagramData.nodes.filter(node => !node.isClass);
diagram.model = new go.GraphLinksModel(nodeDataArray);
