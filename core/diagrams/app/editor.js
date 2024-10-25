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

function updateLink(obj, type=null, fromArrow=null, toArrow=null, fill=colors.black, strokeDashArray=null){
    let model = obj.diagram.model;
    let linkData = obj.part.data;
    model.startTransaction("update link");
    model.setDataProperty(linkData, "type", type);
    model.setDataProperty(linkData, "fromArrow", fromArrow);
    model.setDataProperty(linkData, "toArrow", toArrow);
    model.setDataProperty(linkData, "fill", fill);
    model.setDataProperty(linkData, "strokeDashArray", strokeDashArray);
    model.commitTransaction("update link");
}

function setInheritanceLink(e, obj){
    updateLink(obj, "inheritance", "BackwardTriangle", null, colors.white);
}

function setCompositionLink(e, obj){
    updateLink(obj, "composition", "Backward", "StretchedDiamond");
}

function setCallLink(e, obj){
    updateLink(obj, "call", "Backward", null, colors.black, [2, 5]);
}

function setUsageLink(e, obj){
    updateLink(obj, "usage", null, null, colors.black, [2, 5]);
}

const diagram = new go.Diagram("DiagramDiv",
    {
      "clickCreatingTool.archetypeNodeData": { text: "New module", color: "lightgray" },
      "commandHandler.archetypeGroupData": { text: "New directory", isGroup: true },
      "undoManager.isEnabled": true,
      "allowTextEdit": true,
      layout: getForceDirectedLayout()
    });

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

const linkContextMenu =
  go.GraphObject.build("ContextMenu")
    .add(
      go.GraphObject.build("ContextMenuButton", { click: setInheritanceLink })
        .add(new go.TextBlock("Inheritance")),
      go.GraphObject.build("ContextMenuButton", { click: setCompositionLink })
        .add(new go.TextBlock("Composition")),
      go.GraphObject.build("ContextMenuButton", { click: setCallLink })
        .add(new go.TextBlock("Call")),
      go.GraphObject.build("ContextMenuButton", { click: setUsageLink })
        .add(new go.TextBlock("Usage"))
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

diagram.groupTemplate =
  new go.Group("Vertical",
      { ungroupable: true })
    .add(
      new go.TextBlock({ font: "bold 12pt sans-serif", editable: true })
        .bindTwoWay("text"),
      new go.Panel("Auto")
        .add(
          new go.Shape({ fill: colors.lightgray, stroke: colors.darkgray}),
          new go.Placeholder({ padding: 5 })
        )
    );

diagram.contextMenu = contextMenu
diagram.linkTemplate.contextMenu = linkContextMenu
diagram.groupTemplate.contextMenu = contextMenu

let modelAsText = readJsonFile(savedDiagramPath);
console.log(modelAsText)
diagram.model = go.Model.fromJson(modelAsText);

function updateText(obj, text=null){
    let model = diagram.model;
    let data = obj.data;
    model.startTransaction("update text");
    model.setDataProperty(data, "text", text);
    if (obj instanceof go.Node) {
        model.setDataProperty(data, "shortInfo", text);
        model.setDataProperty(data, "fullInfo", text);
    }
    model.commitTransaction("update text");
}

diagram.addModelChangedListener(function(evt) {
  if (!evt.isTransactionFinished) return;
  if (evt.oc !== "TextEditing") return;

  let transaction = evt.object;
  if (transaction === null) return;

  console.log(transaction.changes)
  let changes = transaction.changes.filter(e => e.diagram !== null)
  console.log(changes)
  changes.each(function(e) {
      let obj = e.diagram.selection.first()
      if (
          (obj instanceof go.Node || obj instanceof go.Link)
          && e.cn === "text"
          && e.du instanceof go.TextBlock
          && e.k instanceof go.Diagram
      ) {
          updateText(obj, changes.r[0].lc)
      }
  });
});
