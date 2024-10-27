let downloadFilename = "diagram"

function showTextInfo(e, obj) {
    digraphDiagram();
    textNodeTemplate(nodeContextMenu);
}

function showShortInfoNode(e, obj) {
    digraphDiagram();
    shortInfoNodeTemplate(nodeContextMenu);
}

function showFullInfoNode(e, obj) {
    digraphDiagram();
    fullInfoNodeTemplate(nodeContextMenu);
}

const contextMenu =
  go.GraphObject.build("ContextMenu")
    .add(
      go.GraphObject.build("ContextMenuButton", { click: showTextInfo })
        .add(new go.TextBlock("Text")),
      go.GraphObject.build("ContextMenuButton", { click: showShortInfoNode })
        .add(new go.TextBlock("Short Info")),
      go.GraphObject.build("ContextMenuButton", { click: showFullInfoNode })
        .add(new go.TextBlock("Full Info")),
      go.GraphObject.build("ContextMenuButton", { click: saveDiagram })
        .add(new go.TextBlock(">    SAVE DIAGRAM    <")),
    );

const nodeContextMenu =
  go.GraphObject.build("ContextMenu")
    .add(
      go.GraphObject.build("ContextMenuButton", { click: showTextInfo })
        .add(new go.TextBlock("Text")),
      go.GraphObject.build("ContextMenuButton", { click: showShortInfoNode })
        .add(new go.TextBlock("Short Info")),
      go.GraphObject.build("ContextMenuButton", { click: showFullInfoNode })
        .add(new go.TextBlock("Full Info"))
    );

showTextInfo()

diagram.contextMenu = contextMenu
diagram.groupTemplate.contextMenu = contextMenu

let modelAsText = readJsonFile(savedDiagramPath);
console.log(modelAsText)
diagram.model = go.Model.fromJson(modelAsText);
