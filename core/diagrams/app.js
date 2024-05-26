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

const diagram =
  new go.Diagram("DiagramDiv",
    {
      "undoManager.isEnabled": true,
    layout: new go.LayeredDigraphLayout({layerSpacing: 200,  columnSpacing: 20 })
    });

function showImports(e, obj) {
    let linkDataArray = diagramData.links.filter(node => node.to === obj.part.data.key);
    let nodeKeys = [obj.part.data.key]
    for (let link of linkDataArray) {
        nodeKeys.push(link.from);
    }
    let nodeDataArray =  diagramData.nodes.filter(node => nodeKeys.includes(node.key));
    diagram.model = new go.GraphLinksModel(nodeDataArray, linkDataArray);
}

function showExports(e, obj) {
    let linkDataArray = diagramData.links.filter(node => node.from === obj.part.data.key);
    let nodeKeys = [obj.part.data.key]
    for (let link of linkDataArray) {
        nodeKeys.push(link.to);
    }
    let nodeDataArray =  diagramData.nodes.filter(node => nodeKeys.includes(node.key));
    diagram.model = new go.GraphLinksModel(nodeDataArray, linkDataArray);
}

function showAllDependencies(e, obj) {
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
    let nodeDataArray =  diagramData.nodes.filter(node => nodeKeys.includes(node.key));
    diagram.model = new go.GraphLinksModel(nodeDataArray, linkDataArray);
}

function showAllModules(e, obj) {
    let nodeDataArray = diagramData.nodes;
    let linkDataArray = diagramData.links;
    diagram.model = new go.GraphLinksModel(nodeDataArray, linkDataArray);
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
    .bind("location", "loc", go.Point.parse)
    .add(
      new go.Shape("RoundedRectangle")
        .bind("fill", "color"),
      new go.TextBlock({ margin: 5, fill: "white" })
        .bind("text", "key")
    );

diagram.linkTemplate =
  new go.Link({
      routing: go.Routing.AvoidsNodes ,
      curve: go.Curve.Bezier,
      mouseEnter: (e, link) => link.elt(0).stroke = "rgba(0,90,156,0.3)",
      mouseLeave: (e, link) => link.elt(0).stroke = "transparent"
    })
    .add(
      new go.Shape( { isPanelMain: true, stroke: "transparent", strokeWidth: 8 }),
      new go.Shape( { isPanelMain: true }),
      new go.Shape( { toArrow: "Standard" }),
      new go.TextBlock({ text: "a Text Block", background: "white", margin: 2 })
        .bind("text")
    );

diagram.contextMenu =
  go.GraphObject.build("ContextMenu")
    .add(
      go.GraphObject.build("ContextMenuButton", { click: showAllModules })
        .add(new go.TextBlock("All modules"))
    );

let nodeDataArray = diagramData.nodes;
let linkDataArray = diagramData.links;

diagram.model = new go.GraphLinksModel(nodeDataArray, linkDataArray);
