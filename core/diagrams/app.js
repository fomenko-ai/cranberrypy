const colors = {
  white: '#FFFFFF',
  black: '#101920',
};

go.Shape.defineArrowheadGeometry('NullPoint', 'm 0,0 l 0,0');
go.Shape.defineArrowheadGeometry('Backward', 'F1 m 8,0 l -2,4 2,4 -8,-4 z');
go.Shape.defineArrowheadGeometry('BackwardTriangle', 'F1 m 8,4 l 0,4 -8,-4 8,-4 0,4 z');
go.Shape.defineArrowheadGeometry('StretchedDiamond', 'F1 m 0,3 l 5,-3 5,3 -5,3 -5,-3 z');



function readTextFile(filePath) {
    let request = new XMLHttpRequest();
    request.open('GET', filePath, false);
    request.send(null);

    if (request.status === 200) {
        return request.responseText;
    } else {
        throw new Error('Unable to load text file at ' + filePath);
    }
}

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

let source_key = readTextFile('./temp/source/source_key');
let diagramData = readJsonFile(`./temp/saved/${source_key}/diagrams.json`)

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

function getNodeDataArray(nodeKeys) {
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

function showClassImports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let linkDataArray = diagramData.links.filter(link => link.to === selectedNodeKey);
    let linkKeys = linkDataArray.map(link => link.from)
    let nodeKeys = [selectedNodeKey].concat(linkKeys)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);
    fullInfoNodeTemplate(nodeClassContextMenu);
}

function showModuleImports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let linkDataArray = diagramData.links.filter(link => (link.to === selectedNodeKey) && !link.isClass);
    let linkKeys = linkDataArray.map(link => link.from)
    let nodeKeys = [selectedNodeKey].concat(linkKeys)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);
    shortInfoNodeTemplate(nodeModuleContextMenu);
}

function showGroupImports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let groupNodesArray = diagramData.nodes.filter(node => (node.group === selectedNodeKey) && node.isModule);
    let groupNodesKeys = groupNodesArray.map(node => node.key)
    let linkDataArray = diagramData.links.filter(link => groupNodesKeys.includes(link.to));
    let nodeKeys = linkDataArray.map(link => link.from)
    nodeKeys = nodeKeys.concat(groupNodesKeys)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);
    textNodeTemplate(nodeGroupContextMenu);
}

function showClassExports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let linkDataArray = diagramData.links.filter(link => link.from === selectedNodeKey);
    let linkKeys = linkDataArray.map(link => link.to)
    let nodeKeys = [selectedNodeKey].concat(linkKeys)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);
    fullInfoNodeTemplate(nodeClassContextMenu);
}

function showModuleExports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let linkDataArray = diagramData.links.filter(link => (link.from === selectedNodeKey) && !link.isClass);
    let linkKeys = linkDataArray.map(link => link.to)
    let nodeKeys = [selectedNodeKey].concat(linkKeys)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);
    shortInfoNodeTemplate(nodeModuleContextMenu);
}

function showGroupExports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let groupNodesArray = diagramData.nodes.filter(node => (node.group === selectedNodeKey) && node.isModule);
    let groupNodesKeys = groupNodesArray.map(node => node.key)
    let linkDataArray = diagramData.links.filter(link => groupNodesKeys.includes(link.from));
    let nodeKeys = linkDataArray.map(link => link.to)
    nodeKeys = nodeKeys.concat(groupNodesKeys)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);
    textNodeTemplate(nodeGroupContextMenu);
}

function showClassDependencies(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let linkDataArray = diagramData.links.filter(
        node => node.to === selectedNodeKey || node.from === selectedNodeKey
    );
    let linkKeys = linkDataArray.map(link => link.from === selectedNodeKey ? link.to : link.from)
    let nodeKeys = [selectedNodeKey].concat(linkKeys)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);
    fullInfoNodeTemplate(nodeClassContextMenu);
}

function showModuleDependencies(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let linkDataArray = diagramData.links.filter(
        node => (node.to === selectedNodeKey || node.from === selectedNodeKey) && !node.isClass
    );
    let linkKeys = linkDataArray.map(link => link.from === selectedNodeKey ? link.to : link.from)
    let nodeKeys = [selectedNodeKey].concat(linkKeys)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);
    shortInfoNodeTemplate(nodeModuleContextMenu);
}

function showGroupDependencies(e, obj) {
    digraphDiagram();
    let selectedNodeKey = obj.part.data.key;
    let groupNodesArray = diagramData.nodes.filter(node => (node.group === selectedNodeKey) && node.isModule);
    let groupNodesKeys = groupNodesArray.map(node => node.key)
    let linkDataArray = diagramData.links.filter(
        link => groupNodesKeys.includes(link.to) || groupNodesKeys.includes(link.from)
    );
    let linkKeys = linkDataArray.map(link => groupNodesKeys.includes(link.from) ? link.to : link.from)
    let nodeKeys = groupNodesKeys.concat(linkKeys)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);
    textNodeTemplate(nodeGroupContextMenu);
}

function showClass(e, obj) {
    forceDirectedDiagram()
    let selectedNode = obj.part.data;
    let selectedNodeKey = selectedNode.key;
    let nodeDataArray = diagramData.nodes.filter(node => node.key === selectedNodeKey);
    let nodeKeys = nodeDataArray.map(node => node.key)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys));
    fullInfoNodeTemplate(nodeClassContextMenu);
}

function showClassModule(e, obj) {
    forceDirectedDiagram()
    let selectedNode = obj.part.data;
    let selectedNodeKey = selectedNode.module;
    let nodeDataArray = diagramData.nodes.filter(node => node.module === selectedNodeKey);
    let nodeKeys = nodeDataArray.map(node => node.key)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys));
    fullInfoNodeTemplate(nodeClassContextMenu);
}

function showModuleClasses(e, obj) {
    forceDirectedDiagram()
    let selectedNode = obj.part.data;
    let selectedNodeKey = selectedNode.key;
    let nodeDataArray = diagramData.nodes.filter(node => node.module === selectedNodeKey);
    if (nodeDataArray) {
        let nodeKeys = nodeDataArray.map(node => node.key)
        diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys));
        fullInfoNodeTemplate(nodeClassContextMenu);
    } else {
        diagram.model = new go.GraphLinksModel(getNodeDataArray([selectedNodeKey]));
        shortInfoNodeTemplate(nodeModuleContextMenu);
    }
}

function showModule(e, obj) {
    forceDirectedDiagram()
    let selectedNode = obj.part.data;
    let selectedNodeKey = selectedNode.key;
    let nodeDataArray = diagramData.nodes.filter(node => node.key === selectedNodeKey);
    let nodeKeys = nodeDataArray.map(node => node.key)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys));
    shortInfoNodeTemplate(nodeModuleContextMenu);
}

function showGroup(e, obj) {
    forceDirectedDiagram();
    let selectedNode = obj.part.data;
    let selectedNodeKey = selectedNode.key;
    let nodeDataArray = diagramData.nodes.filter(node => (node.group === selectedNodeKey || node.key === selectedNodeKey) && !node.isClass);
    diagram.model = new go.GraphLinksModel(nodeDataArray);
    textNodeTemplate(nodeGroupContextMenu);
}

function showGroupModulesByKey(selectedGroupKey){
    function _showGroupModulesByKey(e, obj) {
        forceDirectedDiagram();
        let nodeDataArray = diagramData.nodes.filter(node => (node.group === selectedGroupKey || node.key === selectedGroupKey) && !node.isClass);
        diagram.model = new go.GraphLinksModel(nodeDataArray);
        textNodeTemplate(nodeModuleContextMenu);
    }
    return _showGroupModulesByKey
}

function showAllModules(e, obj) {
    forceDirectedDiagram()
    let nodeDataArray = diagramData.nodes.filter(node => !node.isClass);
    diagram.model = new go.GraphLinksModel(nodeDataArray);
    textNodeTemplate(nodeModuleContextMenu)
}

const nodeClassContextMenu =
  go.GraphObject.build("ContextMenu")
    .add(
      go.GraphObject.build("ContextMenuButton", { click: showClass })
        .add(new go.TextBlock(". . . CLASS . . .")),
      go.GraphObject.build("ContextMenuButton", { click: showClassDependencies })
        .add(new go.TextBlock("Dependencies")),
      go.GraphObject.build("ContextMenuButton", { click: showClassImports })
        .add(new go.TextBlock("Imports")),
      go.GraphObject.build("ContextMenuButton", { click: showClassExports })
        .add(new go.TextBlock("Exports")),
      go.GraphObject.build("ContextMenuButton", { click: showClassModule })
        .add(new go.TextBlock("Module")),
      go.GraphObject.build("ContextMenuButton", { click: showAllModules })
        .add(new go.TextBlock("All modules"))
    );

const nodeModuleContextMenu =
  go.GraphObject.build("ContextMenu")
    .add(
      go.GraphObject.build("ContextMenuButton", { click: showModule })
        .add(new go.TextBlock(". . . MODULE . . .")),
      go.GraphObject.build("ContextMenuButton", { click: showModuleClasses })
        .add(new go.TextBlock("Classes")),
      go.GraphObject.build("ContextMenuButton", { click: showModuleDependencies })
        .add(new go.TextBlock("Dependencies")),
      go.GraphObject.build("ContextMenuButton", { click: showModuleImports })
        .add(new go.TextBlock("Imports")),
      go.GraphObject.build("ContextMenuButton", { click: showModuleExports })
        .add(new go.TextBlock("Exports")),
      go.GraphObject.build("ContextMenuButton", { click: showAllModules })
        .add(new go.TextBlock("All modules"))
    );

const nodeGroupContextMenu =
  go.GraphObject.build("ContextMenu")
    .add(
      go.GraphObject.build("ContextMenuButton", { click: showGroup })
        .add(new go.TextBlock(". . . DIRECTORY . . .")),
      go.GraphObject.build("ContextMenuButton", { click: showGroup })
        .add(new go.TextBlock("Modules")),
      go.GraphObject.build("ContextMenuButton", { click: showGroupDependencies })
        .add(new go.TextBlock("Dependencies")),
      go.GraphObject.build("ContextMenuButton", { click: showGroupImports })
        .add(new go.TextBlock("Imports")),
      go.GraphObject.build("ContextMenuButton", { click: showGroupExports })
        .add(new go.TextBlock("Exports")),
      go.GraphObject.build("ContextMenuButton", { click: showAllModules })
        .add(new go.TextBlock("All modules"))
    );

textNodeTemplate(nodeModuleContextMenu);
diagram.groupTemplate.contextMenu = nodeGroupContextMenu
diagram.linkTemplate =
  new go.Link({
      routing: go.Routing.AvoidsNodes,
      curve: go.Curve.JumpGap,
      mouseEnter: (e, link) => link.elt(0).stroke = "rgba(0,90,156,0.3)",
      mouseLeave: (e, link) => link.elt(0).stroke = "transparent"
    })
    .add(
      new go.Shape( { isPanelMain: true, stroke: "transparent", strokeWidth: 8 }),
      new go.Shape( { isPanelMain: true}).bind("strokeDashArray"),
      new go.Shape({toArrow: "NullPoint", scale: 2, stroke: colors.black}).bind("toArrow").bind("fill"),
      new go.Shape({fromArrow: "NullPoint", scale: 2, stroke: colors.black}).bind("fromArrow").bind("fill"),
      new go.TextBlock({ text: "Text Block", background: "white", margin: 2 })
        .bind("text")
    );

function getGroupContextMenu(groups){
    let menu = [
        go.GraphObject.build("ContextMenuButton", { click: showAllModules })
        .add(new go.TextBlock(". . . . . . . PROJECT . . . . . . .")),
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
            go.GraphObject.build("ContextMenuButton", { click: showGroupModulesByKey(key) })
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
