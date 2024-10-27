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


diagram.linkTemplate.contextMenu = linkContextMenu

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

  let changes = transaction.changes.filter(e => e.diagram !== null)
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
