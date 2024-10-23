let source_key = readTextFile('./temp/source/source_key');
let downloadFilename = source_key
let diagramData = readJsonFile(`./temp/saved/${source_key}/diagrams.json`)

console.log(diagramData)


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

function getSelectedNodeKey(obj){
    let key = obj.part.data.key
    downloadFilename = key.replaceAll('.', '_');
    return key;
}

function showClassImports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = getSelectedNodeKey(obj);
    let linkDataArray = diagramData.links.filter(link => link.to === selectedNodeKey);
    let linkKeys = linkDataArray.map(link => link.from)
    let nodeKeys = [selectedNodeKey].concat(linkKeys)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);
    fullInfoNodeTemplate(nodeClassContextMenu);
}

function showModuleImports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = getSelectedNodeKey(obj);
    let linkDataArray = diagramData.links.filter(link => (link.to === selectedNodeKey) && !link.isClass);
    let linkKeys = linkDataArray.map(link => link.from)
    let nodeKeys = [selectedNodeKey].concat(linkKeys)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);
    shortInfoNodeTemplate(nodeModuleContextMenu);
}

function showGroupImports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = getSelectedNodeKey(obj);
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
    let selectedNodeKey = getSelectedNodeKey(obj);
    let linkDataArray = diagramData.links.filter(link => link.from === selectedNodeKey);
    let linkKeys = linkDataArray.map(link => link.to)
    let nodeKeys = [selectedNodeKey].concat(linkKeys)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);
    fullInfoNodeTemplate(nodeClassContextMenu);
}

function showModuleExports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = getSelectedNodeKey(obj);
    let linkDataArray = diagramData.links.filter(link => (link.from === selectedNodeKey) && !link.isClass);
    let linkKeys = linkDataArray.map(link => link.to)
    let nodeKeys = [selectedNodeKey].concat(linkKeys)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys), linkDataArray);
    shortInfoNodeTemplate(nodeModuleContextMenu);
}

function showGroupExports(e, obj) {
    digraphDiagram();
    let selectedNodeKey = getSelectedNodeKey(obj);
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
    let selectedNodeKey = getSelectedNodeKey(obj);
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
    let selectedNodeKey = getSelectedNodeKey(obj);
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
    let selectedNodeKey = getSelectedNodeKey(obj);
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
    let selectedNodeKey = getSelectedNodeKey(obj);
    let nodeDataArray = diagramData.nodes.filter(node => node.key === selectedNodeKey);
    let nodeKeys = nodeDataArray.map(node => node.key)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys));
    fullInfoNodeTemplate(nodeClassContextMenu);
}

function showClassModule(e, obj) {
    forceDirectedDiagram()
    let selectedNode = obj.part.data;
    let selectedNodeKey = selectedNode.module;
    downloadFilename = selectedNodeKey.replaceAll('.', '_');
    let nodeDataArray = diagramData.nodes.filter(node => node.module === selectedNodeKey);
    let nodeKeys = nodeDataArray.map(node => node.key)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys));
    fullInfoNodeTemplate(nodeClassContextMenu);
}

function showModuleClasses(e, obj) {
    forceDirectedDiagram()
    let selectedNodeKey = getSelectedNodeKey(obj);
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
    let selectedNodeKey = getSelectedNodeKey(obj);
    let nodeDataArray = diagramData.nodes.filter(node => node.key === selectedNodeKey);
    let nodeKeys = nodeDataArray.map(node => node.key)
    diagram.model = new go.GraphLinksModel(getNodeDataArray(nodeKeys));
    shortInfoNodeTemplate(nodeModuleContextMenu);
}

function showGroup(e, obj) {
    forceDirectedDiagram();
    let selectedNodeKey = getSelectedNodeKey(obj);
    let nodeDataArray = diagramData.nodes.filter(node => (node.group === selectedNodeKey || node.key === selectedNodeKey) && !node.isClass);
    diagram.model = new go.GraphLinksModel(nodeDataArray);
    textNodeTemplate(nodeGroupContextMenu);
}

function showGroupModulesByKey(selectedGroupKey){
    function _showGroupModulesByKey(e, obj) {
        forceDirectedDiagram();
        downloadFilename = selectedGroupKey.replaceAll('.', '_');
        let nodeDataArray = diagramData.nodes.filter(node => (node.group === selectedGroupKey || node.key === selectedGroupKey) && !node.isClass);
        diagram.model = new go.GraphLinksModel(nodeDataArray);
        textNodeTemplate(nodeModuleContextMenu);
    }
    return _showGroupModulesByKey
}

function showAllModules(e, obj) {
    forceDirectedDiagram()
    downloadFilename = source_key
    let nodeDataArray = diagramData.nodes.filter(node => !node.isClass);
    diagram.model = new go.GraphLinksModel(nodeDataArray);
    textNodeTemplate(nodeModuleContextMenu);
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
      mouseLeave: (e, link) => link.elt(0).stroke = "transparent",
      relinkableFrom: true, relinkableTo: true
    })
    .add(
      new go.Shape( { isPanelMain: true, stroke: "transparent", strokeWidth: 8 }),
      new go.Shape( { isPanelMain: true}).bind("strokeDashArray"),
      new go.Shape({toArrow: "NullPoint", scale: 2, stroke: colors.black}).bind("toArrow").bind("fill"),
      new go.Shape({fromArrow: "NullPoint", scale: 2, stroke: colors.black}).bind("fromArrow").bind("fill"),
      new go.TextBlock({ text: "Identifier", background: "white", margin: 2, editable: true })
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
    menu.push(
        go.GraphObject.build("ContextMenuButton", { click: saveDiagram })
        .add(new go.TextBlock(">    SAVE DIAGRAM    <"))
    )
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
