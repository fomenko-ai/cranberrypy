let source_key = readTextFile('./temp/source/source_key');
let downloadFilename = source_key
let diagramData = readJsonFile(`./temp/saved/${source_key}/diagrams.json`)

console.log(diagramData)

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

// function showGroupModulesByKey(selectedGroupKey){
//     function _showGroupModulesByKey(e, obj) {
//         forceDirectedDiagram();
//         downloadFilename = selectedGroupKey.replaceAll('.', '_');
//         let nodeDataArray = diagramData.nodes.filter(node => (node.group === selectedGroupKey || node.key === selectedGroupKey) && !node.isClass);
//         diagram.model = new go.GraphLinksModel(nodeDataArray);
//         textNodeTemplate(nodeModuleContextMenu);
//     }
//     return _showGroupModulesByKey
// }

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
        .add(new go.TextBlock(". . . CLASS . . .", buttonStyle)),
      go.GraphObject.build("ContextMenuButton", { click: showClassDependencies })
        .add(new go.TextBlock("Dependencies", buttonStyle)),
      go.GraphObject.build("ContextMenuButton", { click: showClassImports })
        .add(new go.TextBlock("Imports", buttonStyle)),
      go.GraphObject.build("ContextMenuButton", { click: showClassExports })
        .add(new go.TextBlock("Exports", buttonStyle)),
      go.GraphObject.build("ContextMenuButton", { click: showClassModule })
        .add(new go.TextBlock("Module", buttonStyle)),
      go.GraphObject.build("ContextMenuButton", { click: showAllModules })
        .add(new go.TextBlock("All modules", buttonStyle))
    );

const nodeModuleContextMenu =
  go.GraphObject.build("ContextMenu")
    .add(
      go.GraphObject.build("ContextMenuButton", { click: showModule })
        .add(new go.TextBlock(". . . MODULE . . .", buttonStyle)),
      go.GraphObject.build("ContextMenuButton", { click: showModuleClasses })
        .add(new go.TextBlock("Classes", buttonStyle)),
      go.GraphObject.build("ContextMenuButton", { click: showModuleDependencies })
        .add(new go.TextBlock("Dependencies", buttonStyle)),
      go.GraphObject.build("ContextMenuButton", { click: showModuleImports })
        .add(new go.TextBlock("Imports", buttonStyle)),
      go.GraphObject.build("ContextMenuButton", { click: showModuleExports })
        .add(new go.TextBlock("Exports", buttonStyle)),
      go.GraphObject.build("ContextMenuButton", { click: showAllModules })
        .add(new go.TextBlock("All modules", buttonStyle))
    );

const nodeGroupContextMenu =
  go.GraphObject.build("ContextMenu")
    .add(
      go.GraphObject.build("ContextMenuButton", { click: showGroup })
        .add(new go.TextBlock(". . . DIRECTORY . . .", buttonStyle)),
      go.GraphObject.build("ContextMenuButton", { click: showGroup })
        .add(new go.TextBlock("Modules", buttonStyle)),
      go.GraphObject.build("ContextMenuButton", { click: showGroupDependencies })
        .add(new go.TextBlock("Dependencies", buttonStyle)),
      go.GraphObject.build("ContextMenuButton", { click: showGroupImports })
        .add(new go.TextBlock("Imports", buttonStyle)),
      go.GraphObject.build("ContextMenuButton", { click: showGroupExports })
        .add(new go.TextBlock("Exports", buttonStyle)),
      go.GraphObject.build("ContextMenuButton", { click: showAllModules })
        .add(new go.TextBlock("All modules", buttonStyle))
    );

textNodeTemplate(nodeModuleContextMenu);
diagram.groupTemplate.contextMenu = nodeGroupContextMenu

// function getGroupContextMenu(groups){
//     let menu = [
//         go.GraphObject.build("ContextMenuButton", { click: showAllModules })
//         .add(new go.TextBlock(". . . . . . . PROJECT . . . . . . .", buttonStyle)),
//         go.GraphObject.build("ContextMenuButton", { click: showAllModules })
//         .add(new go.TextBlock("All modules", buttonStyle))
//     ];
//     let defaultKeys = ["built_in", "third_party"];
//     let groupKeys = [];
//     for (let group of groups) {
//         if (!defaultKeys.includes(group.key)) {
//             groupKeys.push(group.key);
//         }
//     }
//     groupKeys.sort();
//     groupKeys = defaultKeys.concat(groupKeys);
//     for (let key of groupKeys) {
//         menu.push(
//             go.GraphObject.build("ContextMenuButton", { click: showGroupModulesByKey(key) })
//                 .add(new go.TextBlock(key, buttonStyle))
//         )
//     }
//     menu.push(
//         go.GraphObject.build("ContextMenuButton", { click: saveDiagram })
//         .add(new go.TextBlock(">    SAVE DIAGRAM    <", buttonStyle))
//     )
//     return menu
// }

// let groupsArray = diagramData.nodes.filter(node => node.isGroup);
// let groupContextMenu = getGroupContextMenu(groupsArray);

function showGroupModulesByKeyHTML(selectedGroupKey) {
    forceDirectedDiagram();
    downloadFilename = selectedGroupKey.replaceAll('.', '_');
    let nodeDataArray = diagramData.nodes.filter(node => (node.group === selectedGroupKey || node.key === selectedGroupKey) && !node.isClass);
    diagram.model = new go.GraphLinksModel(nodeDataArray);
    textNodeTemplate(nodeModuleContextMenu);
    diagram.currentTool.stopTool();
}

function showAllModulesHTML() {
    forceDirectedDiagram()
    downloadFilename = source_key
    let nodeDataArray = diagramData.nodes.filter(node => !node.isClass);
    diagram.model = new go.GraphLinksModel(nodeDataArray);
    textNodeTemplate(nodeModuleContextMenu);
}

function createNestedGroupMenu(groupDict, parentKey = '', groupKey = '') {
    let newGroupKey = `${groupKey}__${parentKey}`
    let html = `<li id="${newGroupKey}" class="menu-item" >>_${parentKey}<ul class="menu">`;
    let itemCount = 0;
    let sortedKeys = Object.keys(groupDict).sort();
    for (let key of sortedKeys) {
        if (
            Object.keys(groupDict[key]).length === 0
            && diagramGroupKeys.includes(key)
        ) {
            html += `<li id="${newGroupKey}__${key}" class="menu-item" onpointerdown="showGroupModulesByKeyHTML('${key}')">${key}</li>`;
            itemCount += 1
        } else {
            html += createNestedGroupMenu(groupDict[key], key, `${newGroupKey}__${key}`);
            itemCount += 1
        }
    }
    html += '</ul>';
    html += '</li>';
    if (itemCount > 0){
        return html;
    } else {
        return '';
    }
}

function createGroupMenu(groupDict) {
    let html = '';
    let defaultKeys = ["built_in", "third_party"]

    html += '<li id="built_in" class="menu-item" onpointerdown="showGroupModulesByKeyHTML(\'built_in\')">built_in</li>';
    html += '<li id="third_party" class="menu-item" onpointerdown="showGroupModulesByKeyHTML(\'third_party\')">third_party</li>';

    let sortedKeys = Object.keys(groupDict).sort();
    for (let key of sortedKeys) {
        if (defaultKeys.includes(key)) {
            continue;
        }
        if (
            Object.keys(groupDict[key]).length === 0
            && diagramGroupKeys.includes(key)
        ) {
            html += `<li id="${key}" class="menu-item" onpointerdown="showGroupModulesByKeyHTML(${key})">${key}</li>`;
        } else {
            html += createNestedGroupMenu(groupDict[key], key, key);
        }
    }

    html += '<li id="all_modules" class="menu-item" onpointerdown="showAllModulesHTML()">ALL MODULES</li>';
    html += '<li id="save_diagram" class="menu-item" onpointerdown="saveDiagram()">SAVE DIAGRAM</li>';

    html += '</ul>';
    return html;
}

const diagramGroupKeys = diagramData.group_keys
document.getElementById('contextGroupMenu').innerHTML = createGroupMenu(diagramData.group_dict);

let cxElement = document.getElementById('contextGroupMenu');

cxElement.addEventListener(
      'contextmenu',
      (e) => {
        e.preventDefault();
        return false;
      },
      false
    );

function hideCX() {
      if (diagram.currentTool instanceof go.ContextMenuTool) {
        diagram.currentTool.doCancel();
      }
    }

function showContextMenu(obj, diagram, tool) {
      let hasMenuItem = true

      if (hasMenuItem) {
        cxElement.classList.add('show-menu');

        let mousePt = diagram.lastInput.viewPoint;
        cxElement.style.left = mousePt.x + 5 + 'px';
        cxElement.style.top = mousePt.y + 'px';
      }

      window.addEventListener('pointerdown', hideCX, true);
    }

function hideContextMenu() {
      cxElement.classList.remove('show-menu');
      window.removeEventListener('pointerdown', hideCX, true);
    }

let contextGroupMenu = new go.HTMLInfo({
      show: showContextMenu,
      hide: hideContextMenu
    });
diagram.contextMenu =  contextGroupMenu

let nodeDataArray = diagramData.nodes.filter(node => !node.isClass);
diagram.model = new go.GraphLinksModel(nodeDataArray);
