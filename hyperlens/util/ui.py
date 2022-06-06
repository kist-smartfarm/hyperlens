from PySide6 import QtGui 

def buildAction(
    parent, 
    text, 
    slot=None,
    shortcut=None, 
    icon=None, 
    tip=None,
    checkable = False, 
    enabled= True, 
    checked = False
): 
    action = QtGui.QAction(text, parent)
    if icon is not None:
        action.setIconText(text.replace(" ", "\n"))
        action.setIcon(icon)
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            action.setShortcuts(shortcut)
        else:
            action.setShortcut(shortcut)
    if tip is not None:
        action.setToolTip(tip)
        action.setStatusTip(tip)
    if slot is not None:
        action.triggered.connect(slot)
    if checkable:
        action.setCheckable(True)

    action.setEnabled(enabled)
    action.setChecked(checked)
    return action
