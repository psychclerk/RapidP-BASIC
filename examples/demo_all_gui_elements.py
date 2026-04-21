from rp_runtime.builtins import *
from rp_runtime.gui import *
from rp_runtime.database import *
from rp_runtime.network import *
from rp_runtime.pycomponents import *
def onload():
    global tabs, tab2, timer1, radioresult, list1, radio1, timelabel, radio3, listlabel, statusbar, button1, label1, selectgroup, tracklabel, check1, tab1, tab3, bottompanel, progressbar1, radiolabel, grid1, helpmenu, check2, mainform, track1, combo1, edit1, progresslabel, aboutitem, filemenu, combolabel, checkresult, testspassed, mainmenu, basicgroup, exititem, radio2, richedit1, listview1
    rp_print("Form loaded successfully")
    populatecontrols()
def populatecontrols():
    global tabs, tab2, timer1, radioresult, list1, radio1, timelabel, radio3, listlabel, statusbar, button1, label1, selectgroup, tracklabel, check1, tab1, tab3, bottompanel, progressbar1, radiolabel, grid1, helpmenu, check2, mainform, track1, combo1, edit1, progresslabel, aboutitem, filemenu, combolabel, checkresult, testspassed, mainmenu, basicgroup, exititem, radio2, richedit1, listview1
    combo1.additems("Option 1", "Option 2", "Option 3", "Option 4")
    combo1.text = "Option 1"
    list1.additems("Item A", "Item B", "Item C", "Item D", "Item E")
    listview1.clear()
    listview1.addcolumn("ID", 50)
    listview1.addcolumn("Name", 150)
    listview1.addcolumn("Value", 100)
    listview1.addcolumn("Status", 100)
    listview1.addrow("1", "Product Alpha", "$99.99", "Active")
    listview1.addrow("2", "Product Beta", "$149.99", "Inactive")
    listview1.addrow("3", "Product Gamma", "$199.99", "Active")
    listview1.addrow("4", "Product Delta", "$249.99", "Pending")
    grid1.rows = 5
    grid1.cols = 3
    grid1.cells[0][0] = "Header 1"
    grid1.cells[1][0] = "Header 2"
    grid1.cells[2][0] = "Header 3"
    grid1.cells[0][1] = "Cell 1,1"
    grid1.cells[1][1] = "Cell 1,2"
    grid1.cells[2][1] = "Cell 1,3"
    track1.position = 50
    check1.checked = 1
    check2.checked = 0
    radio1.checked = 1
    radio2.checked = 0
    radio3.checked = 0
    testspassed = (testspassed + 1)
    rp_print("PASS: All controls populated")
def oncombochange():
    global tabs, tab2, timer1, radioresult, list1, radio1, timelabel, radio3, listlabel, statusbar, button1, label1, selectgroup, tracklabel, check1, tab1, tab3, bottompanel, progressbar1, radiolabel, grid1, helpmenu, check2, mainform, track1, combo1, edit1, progresslabel, aboutitem, filemenu, combolabel, checkresult, testspassed, mainmenu, basicgroup, exititem, radio2, richedit1, listview1
    rp_print(("ComboBox changed to: " + combo1.text))
def onlistclick():
    global tabs, tab2, timer1, radioresult, list1, radio1, timelabel, radio3, listlabel, statusbar, button1, label1, selectgroup, tracklabel, check1, tab1, tab3, bottompanel, progressbar1, radiolabel, grid1, helpmenu, check2, mainform, track1, combo1, edit1, progresslabel, aboutitem, filemenu, combolabel, checkresult, testspassed, mainmenu, basicgroup, exititem, radio2, richedit1, listview1
    rp_print(("ListBox selected index: " + str_func(list1.itemindex)))
def onlistviewchange():
    global tabs, tab2, timer1, radioresult, list1, radio1, timelabel, radio3, listlabel, statusbar, button1, label1, selectgroup, tracklabel, check1, tab1, tab3, bottompanel, progressbar1, radiolabel, grid1, helpmenu, check2, mainform, track1, combo1, edit1, progresslabel, aboutitem, filemenu, combolabel, checkresult, testspassed, mainmenu, basicgroup, exititem, radio2, richedit1, listview1
    idx = 0
    idx = listview1.selectedindex
    if (idx >= 0):
        rp_print(("ListView selected row: " + str_func(idx)))
def ontrackchange():
    global tabs, tab2, timer1, radioresult, list1, radio1, timelabel, radio3, listlabel, statusbar, button1, label1, selectgroup, tracklabel, check1, tab1, tab3, bottompanel, progressbar1, radiolabel, grid1, helpmenu, check2, mainform, track1, combo1, edit1, progresslabel, aboutitem, filemenu, combolabel, checkresult, testspassed, mainmenu, basicgroup, exititem, radio2, richedit1, listview1
    tracklabel.caption = ("TrackBar Value: " + str_func(track1.position))
def oncheckchange():
    global tabs, tab2, timer1, radioresult, list1, radio1, timelabel, radio3, listlabel, statusbar, button1, label1, selectgroup, tracklabel, check1, tab1, tab3, bottompanel, progressbar1, radiolabel, grid1, helpmenu, check2, mainform, track1, combo1, edit1, progresslabel, aboutitem, filemenu, combolabel, checkresult, testspassed, mainmenu, basicgroup, exititem, radio2, richedit1, listview1
    if (check1.checked == 1):
        checkresult.caption = "CheckBox is CHECKED"
    else:
        checkresult.caption = "CheckBox is UNCHECKED"
def onradioclick():
    global tabs, tab2, timer1, radioresult, list1, radio1, timelabel, radio3, listlabel, statusbar, button1, label1, selectgroup, tracklabel, check1, tab1, tab3, bottompanel, progressbar1, radiolabel, grid1, helpmenu, check2, mainform, track1, combo1, edit1, progresslabel, aboutitem, filemenu, combolabel, checkresult, testspassed, mainmenu, basicgroup, exititem, radio2, richedit1, listview1
    if (radio1.checked == 1):
        radioresult.caption = "Radio 1 selected"
    elif (radio2.checked == 1):
        radioresult.caption = "Radio 2 selected"
    else:
        radioresult.caption = "Radio 3 selected"
def onbuttonclick():
    global tabs, tab2, timer1, radioresult, list1, radio1, timelabel, radio3, listlabel, statusbar, button1, label1, selectgroup, tracklabel, check1, tab1, tab3, bottompanel, progressbar1, radiolabel, grid1, helpmenu, check2, mainform, track1, combo1, edit1, progresslabel, aboutitem, filemenu, combolabel, checkresult, testspassed, mainmenu, basicgroup, exititem, radio2, richedit1, listview1
    MsgBox("Button was clicked!", "Button Click Event")
    sound(1000, 100)
def ontabchange():
    global tabs, tab2, timer1, radioresult, list1, radio1, timelabel, radio3, listlabel, statusbar, button1, label1, selectgroup, tracklabel, check1, tab1, tab3, bottompanel, progressbar1, radiolabel, grid1, helpmenu, check2, mainform, track1, combo1, edit1, progresslabel, aboutitem, filemenu, combolabel, checkresult, testspassed, mainmenu, basicgroup, exititem, radio2, richedit1, listview1
    rp_print(("Tab changed to: " + tabs.caption))
def ontimertick():
    global tabs, tab2, timer1, radioresult, list1, radio1, timelabel, radio3, listlabel, statusbar, button1, label1, selectgroup, tracklabel, check1, tab1, tab3, bottompanel, progressbar1, radiolabel, grid1, helpmenu, check2, mainform, track1, combo1, edit1, progresslabel, aboutitem, filemenu, combolabel, checkresult, testspassed, mainmenu, basicgroup, exititem, radio2, richedit1, listview1
    timelabel.caption = ("Current Time: " + time_func())
def onexit():
    global tabs, tab2, timer1, radioresult, list1, radio1, timelabel, radio3, listlabel, statusbar, button1, label1, selectgroup, tracklabel, check1, tab1, tab3, bottompanel, progressbar1, radiolabel, grid1, helpmenu, check2, mainform, track1, combo1, edit1, progresslabel, aboutitem, filemenu, combolabel, checkresult, testspassed, mainmenu, basicgroup, exititem, radio2, richedit1, listview1
    mainform.close()
# Directive: $TYPECHECK ON 
rp_print("RapidP Complete GUI Elements Demo")
rp_print("==================================")
rp_print("")
mainform = None
testspassed = 0
testspassed = 0
mainform = PForm()
mainform.caption = "RapidP GUI Elements Demo"
mainform.width = 850
mainform.height = 700
mainform.center()
mainform.onload = onload
mainmenu = PMainMenu(parent=mainform)
filemenu = PMenuItem(parent=mainmenu)
filemenu.caption = "&File"
exititem = PMenuItem(parent=filemenu)
exititem.caption = "E&xit"
exititem.onclick = onexit
helpmenu = PMenuItem(parent=mainmenu)
helpmenu.caption = "&Help"
aboutitem = PMenuItem(parent=helpmenu)
aboutitem.caption = "&About"
basicgroup = PGroupBox(parent=mainform)
basicgroup.caption = "Basic Controls"
basicgroup.left = 10
basicgroup.top = 30
basicgroup.width = 400
basicgroup.height = 200
label1 = PLabel(parent=basicgroup)
label1.caption = "Standard Label:"
label1.left = 10
label1.top = 20
edit1 = PEdit(parent=basicgroup)
edit1.left = 120
edit1.top = 18
edit1.width = 200
edit1.text = "Editable text field"
button1 = PButton(parent=basicgroup)
button1.caption = "Click Me!"
button1.left = 10
button1.top = 50
button1.width = 100
button1.onclick = onbuttonclick
combolabel = PLabel(parent=basicgroup)
combolabel.caption = "ComboBox:"
combolabel.left = 10
combolabel.top = 90
combo1 = PComboBox(parent=basicgroup)
combo1.left = 120
combo1.top = 88
combo1.width = 200
combo1.onchange = oncombochange
listlabel = PLabel(parent=basicgroup)
listlabel.caption = "ListBox:"
listlabel.left = 10
listlabel.top = 125
list1 = PListBox(parent=basicgroup)
list1.left = 120
list1.top = 120
list1.width = 200
list1.height = 60
list1.onclick = onlistclick
selectgroup = PGroupBox(parent=mainform)
selectgroup.caption = "Selection Controls"
selectgroup.left = 420
selectgroup.top = 30
selectgroup.width = 400
selectgroup.height = 200
check1 = PCheckBox(parent=selectgroup)
check1.caption = "Enable Feature"
check1.left = 10
check1.top = 20
check1.onchange = oncheckchange
checkresult = PLabel(parent=selectgroup)
checkresult.caption = ""
checkresult.left = 150
checkresult.top = 20
checkresult.width = 200
check2 = PCheckBox(parent=selectgroup)
check2.caption = "Another Option"
check2.left = 10
check2.top = 50
radiolabel = PLabel(parent=selectgroup)
radiolabel.caption = "Radio Buttons:"
radiolabel.left = 10
radiolabel.top = 85
radio1 = PRadioButton(parent=selectgroup)
radio1.caption = "Option 1"
radio1.left = 10
radio1.top = 110
radio1.onclick = onradioclick
radio2 = PRadioButton(parent=selectgroup)
radio2.caption = "Option 2"
radio2.left = 100
radio2.top = 110
radio2.onclick = onradioclick
radio3 = PRadioButton(parent=selectgroup)
radio3.caption = "Option 3"
radio3.left = 200
radio3.top = 110
radio3.onclick = onradioclick
radioresult = PLabel(parent=selectgroup)
radioresult.caption = ""
radioresult.left = 10
radioresult.top = 145
radioresult.width = 200
tracklabel = PLabel(parent=selectgroup)
tracklabel.caption = "TrackBar Value: 50"
tracklabel.left = 10
tracklabel.top = 170
track1 = PTrackBar(parent=selectgroup)
track1.left = 150
track1.top = 165
track1.width = 200
track1.min = 0
track1.max = 100
track1.position = 50
track1.onchange = ontrackchange
tabs = PTabControl(parent=mainform)
tabs.left = 10
tabs.top = 240
tabs.width = 810
tabs.height = 300
tabs.onchange = ontabchange
tab1 = PTabItem(parent=tabs)
tab1.caption = "Data View"
listview1 = PListView(parent=tab1)
listview1.left = 10
listview1.top = 30
listview1.width = 780
listview1.height = 250
listview1.onchange = onlistviewchange
tab2 = PTabItem(parent=tabs)
tab2.caption = "Grid View"
grid1 = PStringGrid(parent=tab2)
grid1.left = 10
grid1.top = 30
grid1.width = 780
grid1.height = 250
tab3 = PTabItem(parent=tabs)
tab3.caption = "Rich Text"
richedit1 = PRichEdit(parent=tab3)
richedit1.left = 10
richedit1.top = 30
richedit1.width = 780
richedit1.height = 250
richedit1.text = (((("This is a rich text editor." + chr(10)) + "You can edit this text.") + chr(10)) + "Multiple lines supported!")
bottompanel = PPanel(parent=mainform)
bottompanel.left = 10
bottompanel.top = 550
bottompanel.width = 810
bottompanel.height = 80
bottompanel.color = 15789568
timelabel = PLabel(parent=bottompanel)
timelabel.caption = "Current Time: "
timelabel.left = 10
timelabel.top = 10
timelabel.fontsize = 11
timelabel.fontbold = 1
timelabel.font.name = "Arial"
progressbar1 = PProgressBar(parent=bottompanel)
progressbar1.left = 150
progressbar1.top = 10
progressbar1.width = 200
progressbar1.height = 20
progressbar1.min = 0
progressbar1.max = 100
progressbar1.position = 75
progresslabel = PLabel(parent=bottompanel)
progresslabel.caption = "Progress: 75%"
progresslabel.left = 360
progresslabel.top = 10
timer1 = PTimer(parent=mainform)
timer1.interval = 1000
timer1.ontimer = ontimertick
statusbar = PStatusBar(parent=mainform)
statusbar.simpletext = "Ready - Demonstrating all GUI elements"
rp_print("GUI Components Demonstrated:")
rp_print("- PForm (Main window)")
rp_print("- PMainMenu & PMenuItem (Menu bar)")
rp_print("- PLabel (Text labels)")
rp_print("- PEdit (Text input)")
rp_print("- PButton (Buttons)")
rp_print("- PGroupBox (Group containers)")
rp_print("- PComboBox (Dropdown lists)")
rp_print("- PListBox (List selections)")
rp_print("- PCheckBox (Boolean toggles)")
rp_print("- PRadioButton (Single selection)")
rp_print("- PTrackBar (Slider control)")
rp_print("- PTabControl & PTabItem (Tabs)")
rp_print("- PListView (Multi-column lists)")
rp_print("- PStringGrid (Spreadsheet-like grid)")
rp_print("- PRichEdit (Rich text editor)")
rp_print("- PPanel (Container panels)")
rp_print("- PProgressBar (Progress indicator)")
rp_print("- PTimer (Timed events)")
rp_print("- PStatusBar (Status display)")
rp_print("")
rp_print("Starting GUI demo...")
rp_print("")
mainform.showmodal()
rp_print("")
rp_print("Demo completed!")