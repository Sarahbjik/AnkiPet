# import the main window object (mw) from aqt
from aqt import mw

# import all of the Qt GUI library
from aqt.qt import *

from . import gameQt

'''
def enterGame():
    # show a dialog box
    gm = gameQt.GameQt()
    gm.showPet()
'''    

def enterGame():
    # show a dialog box
    gm.showPet()
    
# create a new menu item
gm = gameQt.GameQt()
action = QAction("AnkiPet", mw)
action.triggered.connect(enterGame)
mw.form.menuTools.addAction(action)



'''
To do list:

- to fix the X button problem use something like this:

import sys
from PyQt4 import QtGui,QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
class Create_Dialog_Box(QDialog):
    def __init__(self,parent = None):
        super(Create_Dialog_Box, self).__init__(parent)
        self.setGeometry(100,100,500,200)
    def closeEvent(self,event):
        quit_msg = "Are you sure you want to exit the dialog?"
        reply = QtGui.QMessageBox.question(self, 'Message', 
                        quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

app = QtGui.QApplication(sys.argv)
w = QtGui.QWidget()
w.setGeometry(100,100,200,50)

d = Create_Dialog_Box(w)

b = QtGui.QPushButton(w)
b.setText("Click Me!")
b.move(50,20)
b.clicked.connect(d.show)


w.setWindowTitle("PyQt")
w.show()
print("End")
sys.exit(app.exec_())


Known bugs:
- quiting anki pet with the X leads to information not being saved
- when not online for a time and getting a lot of 0 entries and not resolving the day but quitting and restarting the game does it give 0 entries again?
- update 3oclock in mornign led to 0 tokens instead of 9 (still true? not encountered since 21-3-2020 at least)

Game Logic:
- death by old age + needs a graphical representation (cemetary of pets???)
- for breeding one needs a farm - need to invest into reputation to get an old farmhouse of your aunt then you have a farm
- breed functionality


Contents:
- with even more reputation your aunt offers you a farm
- adult animals get sick when they are not cared for + drawing for that
- different color grown up animals for breeding with genes
- farm


'''