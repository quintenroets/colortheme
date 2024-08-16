function toArray(elements) {
    let elementsString = elements.toString();
    let elementsArray = elementsString.length > 0 ? elementsString.split(",") : [];
    return elementsArray;
}

let panel = panels()[0];
let widgets = toArray(panel.widgetIds).map(id => panel.widgetById(Number(id)));
let widget = widgets.filter(widget => widget.type == "org.kde.plasma.kickoff")[0];
widget.currentConfigGroup  = "General";
let iconPath =  widget.readConfig("icon");
print(iconPath);
