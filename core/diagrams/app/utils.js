const colors = {
  white: '#FFFFFF',
  black: '#101920',
  lightgray: '#D0D0D0',
  darkgray: '#B0B0B0'
};

go.Shape.defineArrowheadGeometry('NullPoint', 'm 0,0 l 0,0');
go.Shape.defineArrowheadGeometry('Standard', 'F1 m 0,0 l 8,4 -8,4 2,-4 z');
go.Shape.defineArrowheadGeometry('Backward', 'F1 m 8,0 l -2,4 2,4 -8,-4 z');
go.Shape.defineArrowheadGeometry('Triangle', 'F1 m 0,0 l 8,4.62 -8,4.62 z');
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

function saveJsonFile(data, filename) {
    const jsonData = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
}

function saveDiagram(e, obj) {
    let data = diagram.model.toJson();
    saveJsonFile(data, downloadFilename)
}

function loadDiagram(e, obj) {
    downloadFilename = source_key
    let modelAsText = readJsonFile(savedDiagramPath);
    diagram.model = go.Model.fromJson(modelAsText);
    textNodeTemplate(nodeModuleContextMenu);
}

function textNodeTemplate(menu){
    diagram.nodeTemplate = new go.Node("Auto", { contextMenu: menu })
    .add(
      new go.Shape("RoundedRectangle", {
            portId: "",
            cursor: "pointer",
            fromLinkable: true, fromLinkableSelfNode: true, fromLinkableDuplicates: true,
            toLinkable: true, toLinkableSelfNode: true, toLinkableDuplicates: true
          })
        .bind("fill", "color"),
      new go.TextBlock({ margin: 5, fill: colors.black, editable: true })
        .bind("text", "text")
    );
}

function shortInfoNodeTemplate(menu){
    diagram.nodeTemplate = new go.Node("Auto", { contextMenu: menu })
    .add(
      new go.Shape("RoundedRectangle", {
            portId: "",
            cursor: "pointer",
            fromLinkable: true, fromLinkableSelfNode: true, fromLinkableDuplicates: true,
            toLinkable: true, toLinkableSelfNode: true, toLinkableDuplicates: true
          })
        .bind("fill", "color"),
      new go.TextBlock({ margin: 5, fill: colors.black, editable: true })
        .bind("text", "shortInfo")
    );
}

function fullInfoNodeTemplate(menu){
    diagram.nodeTemplate = new go.Node("Auto", { contextMenu: menu })
    .add(
      new go.Shape("RoundedRectangle", {
            portId: "",
            cursor: "pointer",
            fromLinkable: true, fromLinkableSelfNode: true, fromLinkableDuplicates: true,
            toLinkable: true, toLinkableSelfNode: true, toLinkableDuplicates: true
          })
        .bind("fill", "color"),
      new go.TextBlock({ margin: 5, fill: colors.black, editable: true })
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
