from rp_runtime.builtins import *
from rp_runtime.gui import *
from rp_runtime.database import *
from rp_runtime.network import *
from rp_runtime.pycomponents import *
def onmainload():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    initdb()
    loaddataintolistview()
    updatestatusbar()
def onexit():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    db.close()
    mainform.close()
def onaddclick():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    cleareditfields()
    currentid = 0
    editframe.visible = 1
def oneditclick():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    idx = 0
    idx = listview1.selectedindex
    if (idx >= 0):
        loadrecordintoedits(idx)
        editframe.visible = 1
    else:
        MsgBox("Please select a record to edit", "Info")
def ondeleteclick():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    idx = 0
    idx = listview1.selectedindex
    if ((idx >= 0) and (currentid > 0)):
        result = 0
        result = MsgBox("Are you sure you want to delete this record?", "Confirm", 1)
        if (result == 1):
            deleterecord()
            loaddataintolistview()
            cleareditfields()
            editframe.visible = 0
    else:
        MsgBox("Please select a record to delete", "Info")
def onsaveclick():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    saverecord()
    loaddataintolistview()
    editframe.visible = 0
    sound(1500, 100)
def oncancelclick():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    editframe.visible = 0
def onlistviewchange():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    idx = 0
    idx = listview1.selectedindex
    if (idx >= 0):
        displayrecorddetails(idx)
        updatebuttonstates()
def onlistviewdblclick():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    oneditclick()
def onrefreshclick():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    loaddataintolistview()
    statusbar.simpletext = ("Data refreshed at " + time_func())
    sound(1000, 50)
def onsearchclick():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    searchterm = ""
    searchterm = searchedit.text
    if (searchterm != ""):
        searchinlistview(searchterm)
def onshowdetailformclick():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    showdetailwindow()
def onshowaboutclick():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    showaboutwindow()
def ontimertick():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    statusbar.simpletext = ((((("RapidP Database Demo | Time: " + time_func()) + " | Date: ") + date_func()) + " | Records: ") + str_func(listview1.itemcount))
def initdb():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    db_name = ""
    db_name = "demo_complete.db"
    if (db.connect(db_name) == 0):
        rp_print("Creating new SQLite database...")
    db.query("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
    if (db.fetchrow() == 0):
        db.query("CREATE TABLE employees (id INTEGER PRIMARY KEY AUTOINCREMENT, firstName VARCHAR(50), lastName VARCHAR(50), email VARCHAR(100), department VARCHAR(50), salary DECIMAL(10,2), hireDate DATE, active INTEGER)")
        db.query("INSERT INTO employees (firstName, lastName, email, department, salary, hireDate, active) VALUES ('John', 'Smith', 'john@email.com', 'IT', 75000.00, '2023-01-15', 1)")
        db.query("INSERT INTO employees (firstName, lastName, email, department, salary, hireDate, active) VALUES ('Sarah', 'Johnson', 'sarah@email.com', 'HR', 65000.00, '2023-02-20', 1)")
        db.query("INSERT INTO employees (firstName, lastName, email, department, salary, hireDate, active) VALUES ('Mike', 'Williams', 'mike@email.com', 'Sales', 80000.00, '2023-03-10', 1)")
        db.query("INSERT INTO employees (firstName, lastName, email, department, salary, hireDate, active) VALUES ('Emily', 'Brown', 'emily@email.com', 'IT', 72000.00, '2023-04-05', 1)")
        db.query("INSERT INTO employees (firstName, lastName, email, department, salary, hireDate, active) VALUES ('David', 'Jones', 'david@email.com', 'Finance', 85000.00, '2023-05-12', 1)")
def loaddataintolistview():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    listview1.clear()
    listview1.clear()
    db.query("SELECT id, firstName, lastName, email, department, salary, active FROM employees ORDER BY id")
    while (db.fetchrow() == 1):
        isactive = ""
        if (val(db.row(6)) == 1):
            isactive = "Yes"
        else:
            isactive = "No"
        listview1.addrow(db.row(0), db.row(1), db.row(2), db.row(3), db.row(4), ("$" + db.row(5)), isactive)
def loadrecordintoedits(idx):
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    db.query("SELECT id, firstName, lastName, email, department, salary, hireDate, active FROM employees ORDER BY id")
    db.rowseek(idx)
    if (db.fetchrow() == 1):
        currentid = val(db.row(0))
        firstnameedit.text = db.row(1)
        lastnameedit.text = db.row(2)
        emailedit.text = db.row(3)
        deptcombobox.text = db.row(4)
        salaryedit.text = db.row(5)
        hiredateedit.text = db.row(6)
        activecheck.checked = val(db.row(7))
def displayrecorddetails(idx):
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    db.query("SELECT id, firstName, lastName, email, department, salary, hireDate, active FROM employees ORDER BY id")
    db.rowseek(idx)
    if (db.fetchrow() == 1):
        detaillabel.caption = ((((((((((((((("Viewing: " + db.row(1)) + " ") + db.row(2)) + chr(10)) + "Email: ") + db.row(3)) + chr(10)) + "Department: ") + db.row(4)) + chr(10)) + "Salary: $") + db.row(5)) + chr(10)) + "Hired: ") + db.row(6))
def saverecord():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    if (currentid > 0):
        q = ""
        q = ((((((((((((((("UPDATE employees SET firstName='" + firstnameedit.text) + "', lastName='") + lastnameedit.text) + "', email='") + emailedit.text) + "', department='") + deptcombobox.text) + "', salary=") + salaryedit.text) + "', hireDate='") + hiredateedit.text) + "', active=") + str_func(activecheck.checked)) + " WHERE id=") + str_func(currentid))
        db.query(q)
    else:
        q = ""
        q = (((((((((((((("INSERT INTO employees (firstName, lastName, email, department, salary, hireDate, active) VALUES ('" + firstnameedit.text) + "', '") + lastnameedit.text) + "', '") + emailedit.text) + "', '") + deptcombobox.text) + "', ") + salaryedit.text) + ", '") + hiredateedit.text) + "', ") + str_func(activecheck.checked)) + ")")
        db.query(q)
def deleterecord():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    if (currentid > 0):
        q = ""
        q = ("DELETE FROM employees WHERE id=" + str_func(currentid))
        db.query(q)
        currentid = 0
def cleareditfields():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    firstnameedit.text = ""
    lastnameedit.text = ""
    emailedit.text = ""
    deptcombobox.text = "IT"
    salaryedit.text = "0"
    hiredateedit.text = date_func()
    activecheck.checked = 1
    currentid = 0
def updatebuttonstates():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    if (listview1.selectedindex >= 0):
        editbtn.enabled = 1
        deletebtn.enabled = 1
    else:
        editbtn.enabled = 0
        deletebtn.enabled = 0
def updatestatusbar():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    statusbar.simpletext = (("Ready - " + str_func(listview1.itemcount)) + " records loaded")
def searchinlistview(term):
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    i = 0
    found = 0
    found = 0
    i = 0
    while i <= (listview1.itemcount - 1):
        itemdata = ""
        itemdata = listview1.getitem(i)
        if (instr(ucase(itemdata), ucase(term)) > 0):
            listview1.selectedindex = i
            found = 1
            break
        i += 1
    if (found == 0):
        MsgBox(("No records found matching: " + term), "Search Results")
def showdetailwindow():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    detailform.showmodal()
def showaboutwindow():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    aboutversionlabel.caption = "Version 1.0.0"
    aboutbuildlabel.caption = ((("Build: " + date_func()) + " ") + time_func())
    aboutdesclabel.caption = (((("A complete demonstration of RapidP GUI components" + chr(10)) + "including ListView, ComboBox, CheckBox,") + chr(10)) + "TabControl, StringGrid, and multi-window support.")
    aboutform.showmodal()
def onclosedetail():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    detailform.close()
def oncloseabout():
    global exititem, closedetailbtn, lastnameedit, firstnamelabel, helpmenu, emaillabel, hiredatelabel, infotabs, salaryedit, salarylabel, detaillabel, aboutdesclabel, lastnamelabel, detailitem, currentid, emailedit, detailimage, viewmenu, aboutcopyright, searchedit, filemenu, activecheck, searchbtn, mainform, editframe, listview1, deletebtn, detailform, hiredateedit, statsgrid, timer1, searchlabel, deptlabel, cancelbtn, mainmenu, statusbar, savebtn, aboutversionlabel, firstnameedit, searchpanel, aboutitem, statslabel, toolbarpanel, abouttitle, addbtn, tab1, refreshbtn, deptcombobox, aboutform, editbtn, tab2, db, closeaboutbtn, aboutbuildlabel, detailwindowbtn
    aboutform.close()
# Directive: $TYPECHECK ON 
db = PSQLite()
currentid = 0
mainform = None
detailform = None
aboutform = None
mainform = PForm()
mainform.caption = "RapidP Complete Database Demo"
mainform.width = 900
mainform.height = 650
mainform.center()
mainform.onload = onmainload
mainmenu = PMainMenu(parent=mainform)
filemenu = PMenuItem(parent=mainmenu)
filemenu.caption = "&File"
exititem = PMenuItem(parent=filemenu)
exititem.caption = "E&xit"
exititem.onclick = onexit
viewmenu = PMenuItem(parent=mainmenu)
viewmenu.caption = "&View"
detailitem = PMenuItem(parent=viewmenu)
detailitem.caption = "&Detail Window"
detailitem.onclick = onshowdetailformclick
helpmenu = PMenuItem(parent=mainmenu)
helpmenu.caption = "&Help"
aboutitem = PMenuItem(parent=helpmenu)
aboutitem.caption = "&About"
aboutitem.onclick = onshowaboutclick
toolbarpanel = PPanel(parent=mainform)
toolbarpanel.top = 0
toolbarpanel.left = 0
toolbarpanel.width = 884
toolbarpanel.height = 50
toolbarpanel.color = 12632256
addbtn = PButton(parent=toolbarpanel)
addbtn.caption = "&Add New"
addbtn.left = 10
addbtn.top = 10
addbtn.width = 80
addbtn.height = 30
addbtn.onclick = onaddclick
editbtn = PButton(parent=toolbarpanel)
editbtn.caption = "&Edit"
editbtn.left = 100
editbtn.top = 10
editbtn.width = 80
editbtn.height = 30
editbtn.onclick = oneditclick
deletebtn = PButton(parent=toolbarpanel)
deletebtn.caption = "&Delete"
deletebtn.left = 190
deletebtn.top = 10
deletebtn.width = 80
deletebtn.height = 30
deletebtn.onclick = ondeleteclick
refreshbtn = PButton(parent=toolbarpanel)
refreshbtn.caption = "&Refresh"
refreshbtn.left = 280
refreshbtn.top = 10
refreshbtn.width = 80
refreshbtn.height = 30
refreshbtn.onclick = onrefreshclick
detailwindowbtn = PButton(parent=toolbarpanel)
detailwindowbtn.caption = "&Detail Window"
detailwindowbtn.left = 370
detailwindowbtn.top = 10
detailwindowbtn.width = 100
detailwindowbtn.height = 30
detailwindowbtn.onclick = onshowdetailformclick
searchpanel = PPanel(parent=mainform)
searchpanel.top = 50
searchpanel.left = 0
searchpanel.width = 884
searchpanel.height = 40
searchlabel = PLabel(parent=searchpanel)
searchlabel.caption = "Search:"
searchlabel.left = 10
searchlabel.top = 12
searchedit = PEdit(parent=searchpanel)
searchedit.left = 60
searchedit.top = 10
searchedit.width = 200
searchbtn = PButton(parent=searchpanel)
searchbtn.caption = "&Find"
searchbtn.left = 270
searchbtn.top = 10
searchbtn.width = 60
searchbtn.onclick = onsearchclick
listview1 = PListView(parent=mainform)
listview1.top = 90
listview1.left = 10
listview1.width = 870
listview1.height = 300
listview1.onchange = onlistviewchange
listview1.ondblclick = onlistviewdblclick
infotabs = PTabControl(parent=mainform)
infotabs.top = 395
infotabs.left = 10
infotabs.width = 870
infotabs.height = 150
tab1 = PTabItem(parent=infotabs)
tab1.caption = "Edit Record"
editframe = PFRAME(parent=tab1)
editframe.left = 5
editframe.top = 25
editframe.width = 850
editframe.height = 110
firstnamelabel = PLabel(parent=editframe)
firstnamelabel.caption = "First Name:"
firstnamelabel.left = 10
firstnamelabel.top = 10
firstnameedit = PEdit(parent=editframe)
firstnameedit.left = 100
firstnameedit.top = 8
firstnameedit.width = 150
lastnamelabel = PLabel(parent=editframe)
lastnamelabel.caption = "Last Name:"
lastnamelabel.left = 270
lastnamelabel.top = 10
lastnameedit = PEdit(parent=editframe)
lastnameedit.left = 360
lastnameedit.top = 8
lastnameedit.width = 150
emaillabel = PLabel(parent=editframe)
emaillabel.caption = "Email:"
emaillabel.left = 10
emaillabel.top = 40
emailedit = PEdit(parent=editframe)
emailedit.left = 100
emailedit.top = 38
emailedit.width = 300
deptlabel = PLabel(parent=editframe)
deptlabel.caption = "Department:"
deptlabel.left = 10
deptlabel.top = 70
deptcombobox = PComboBox(parent=editframe)
deptcombobox.left = 100
deptcombobox.top = 68
deptcombobox.width = 150
salarylabel = PLabel(parent=editframe)
salarylabel.caption = "Salary:"
salarylabel.left = 270
salarylabel.top = 70
salaryedit = PEdit(parent=editframe)
salaryedit.left = 360
salaryedit.top = 68
salaryedit.width = 100
hiredatelabel = PLabel(parent=editframe)
hiredatelabel.caption = "Hire Date:"
hiredatelabel.left = 480
hiredatelabel.top = 70
hiredateedit = PEdit(parent=editframe)
hiredateedit.left = 560
hiredateedit.top = 68
hiredateedit.width = 100
activecheck = PCheckBox(parent=editframe)
activecheck.caption = "Active"
activecheck.left = 680
activecheck.top = 70
activecheck.checked = 1
savebtn = PButton(parent=editframe)
savebtn.caption = "&Save"
savebtn.left = 750
savebtn.top = 5
savebtn.width = 80
savebtn.onclick = onsaveclick
cancelbtn = PButton(parent=editframe)
cancelbtn.caption = "&Cancel"
cancelbtn.left = 750
cancelbtn.top = 40
cancelbtn.width = 80
cancelbtn.onclick = oncancelclick
tab2 = PTabItem(parent=infotabs)
tab2.caption = "Statistics"
statslabel = PLabel(parent=tab2)
statslabel.caption = "Employee Statistics will appear here"
statslabel.left = 20
statslabel.top = 30
statsgrid = PStringGrid(parent=tab2)
statsgrid.left = 20
statsgrid.top = 50
statsgrid.width = 800
statsgrid.height = 80
statsgrid.cols = 2
statsgrid.rows = 4
statusbar = PStatusBar(parent=mainform)
statusbar.simpletext = "Initializing..."
timer1 = PTimer(parent=mainform)
timer1.interval = 1000
timer1.ontimer = ontimertick
detailform = PForm()
detailform.caption = "Employee Details"
detailform.width = 400
detailform.height = 300
detailform.center()
detailform.borderstyle = 1
detaillabel = PLabel(parent=detailform)
detaillabel.caption = "Select an employee to view details"
detaillabel.left = 20
detaillabel.top = 20
detaillabel.width = 350
detaillabel.height = 100
detaillabel.alignment = 0
detailimage = PImage(parent=detailform)
detailimage.left = 150
detailimage.top = 130
detailimage.width = 100
detailimage.height = 100
closedetailbtn = PButton(parent=detailform)
closedetailbtn.caption = "Close"
closedetailbtn.left = 160
closedetailbtn.top = 240
closedetailbtn.width = 80
closedetailbtn.onclick = onclosedetail
aboutform = PForm()
aboutform.caption = "About RapidP Database Demo"
aboutform.width = 400
aboutform.height = 300
aboutform.center()
aboutform.borderstyle = 1
aboutform.modal = 1
abouttitle = PLabel(parent=aboutform)
abouttitle.caption = "RapidP Database Application"
abouttitle.left = 20
abouttitle.top = 20
abouttitle.width = 350
abouttitle.fontsize = 14
abouttitle.fontbold = 1
aboutversionlabel = PLabel(parent=aboutform)
aboutversionlabel.caption = "Version 1.0.0"
aboutversionlabel.left = 20
aboutversionlabel.top = 50
aboutbuildlabel = PLabel(parent=aboutform)
aboutbuildlabel.caption = "Build: "
aboutbuildlabel.left = 20
aboutbuildlabel.top = 75
aboutdesclabel = PLabel(parent=aboutform)
aboutdesclabel.caption = "A demonstration application"
aboutdesclabel.left = 20
aboutdesclabel.top = 100
aboutdesclabel.width = 350
aboutdesclabel.height = 80
aboutdesclabel.multiline = 1
aboutcopyright = PLabel(parent=aboutform)
aboutcopyright.caption = "© 2024 RapidP Demo"
aboutcopyright.left = 20
aboutcopyright.top = 200
closeaboutbtn = PButton(parent=aboutform)
closeaboutbtn.caption = "OK"
closeaboutbtn.left = 160
closeaboutbtn.top = 230
closeaboutbtn.width = 80
closeaboutbtn.onclick = oncloseabout
deptcombobox.additems("IT", "HR", "Sales", "Finance", "Marketing", "Operations")
statsgrid.cells[0][0] = "Statistic"
statsgrid.cells[1][0] = "Value"
statsgrid.cells[0][1] = "Total Employees"
statsgrid.cells[0][2] = "Departments"
statsgrid.cells[0][3] = "Active"
rp_print("Starting RapidP Complete Database Demo...")
rp_print("This demo showcases:")
rp_print("- ListView with multiple columns")
rp_print("- ComboBox, CheckBox, Edit controls")
rp_print("- TabControl with multiple tabs")
rp_print("- StringGrid for displaying tabular data")
rp_print("- Multi-window support (modal dialogs)")
rp_print("- Full CRUD database operations")
rp_print("- Event handling for all controls")
rp_print("")
mainform.showmodal()
rp_print("Application closed.")