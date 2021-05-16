# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *
from . import game

import math
import json



class GameQt():

    def __init__(self):
         # clear the debug file (mode w+)
        debug_file=open(mw.pm.addonFolder()+"\\AnkiPet\\debug\\debugfile.txt","w+")
        debug_file.write("Starting to __init__() GameQT")
        debug_file.close()
        self.game=game.Game()
        self.pet_layout = QHBoxLayout()
        self.util = Util()
        self.util.debug("Finished __init__() of gameQt")
    
    def showPet(self):
        self.util.debug("gameQt.showPet() start")
    
        self.diag = QDialog()
        self.diag.setWindowTitle("AnkiPet")

        self.diag.setMinimumHeight(700)
        self.diag.setMinimumWidth(700)   
        

        self.layout = QVBoxLayout(self.diag)
        self.diag.setLayout(self.layout)
        text = QTextBrowser()
        text.setFontPointSize(12)
        
        self.util.debug("gameQt.showPet() start to retrieve stats info")
        text.setPlainText(self.statsDiag())
        self.layout.addWidget(text)
    
    
        def resolveDayBtn():
            self.game.resolveDay()
            text.setPlainText(self.statsDiag())
            self.update_renderPet2()
        btn = QPushButton(_("Resolve day"))
        btn.clicked.connect(resolveDayBtn)
        box=QDialogButtonBox(QDialogButtonBox.Close)
        self.layout.addWidget(box)
        box.addButton(btn, QDialogButtonBox.ActionRole)
        
        def onReject():
            self.game.save_pets()
            QDialog.reject(self.diag)
        box.rejected.connect(onReject)
        box.accepted.connect(onReject)
        
        self.util.debug("gameQt.showPet() finished with window and buttons")
        
        self.renderPet2()
        self.util.debug("gameQt.showPet() finished rendering the pets")
        
        if self.game.check_for_game_event():
            text.setPlainText(self.statsDiag())
            self.game_event()
            self.update_renderPet2()
        self.util.debug("gameQt.showPet() finished check for event")
        
        # add game logic before this line
        self.diag.exec_()
    
        
        
        
    def statsDiag(self):
        stats = self.game.getTodayStats()
        frac=stats[2]*100
        tok=int(math.sqrt(frac))
        progress =self.game.factor(tok)
        line="Current progress today: "+'{:.2f}'.format(progress)+" days.\nTo do: "+str(stats[0])+"          Done today:"+str(stats[1])+"          Fraction done: "+ \
            str(frac)[:4]+"%\nReputation: "+str(stats[4]) + "\nThe mood in your stable currently is "+self.game.stable_mood
        self.util.debug("gameQt.showPet() finished retrieving stats: "+line)
        return line
        
        
    def renderPet2(self):
        self.pet_view=QListView(self.diag)
        self.pet_view.setMinimumSize(550, 600)
        
        self.model = QStandardItemModel(self.pet_view)
        self.pet_view.setIconSize(QSize(400,500))
        
        for pet_entry in self.game.pet_objects:
            self.model.appendRow(pet_entry.get_image())
            
        self.pet_view.setModel(self.model)
        
        def name_pet(index):
            d = QDialog()
            d.setMinimumHeight(70)
            d.setMinimumWidth(200)
            d.setWindowTitle("Name your pet")
            
            e1 = QLineEdit()
            e1.setMaxLength(40)
            e1.setFont(QFont("Arial",12))
            def name_changed(text):
                self.game.name_this_pet(text,index.row())
                self.update_renderPet2()
            e1.textChanged.connect(name_changed)
            
            flo = QFormLayout()
            flo.addRow("Enter a name for your pet:", e1)
            d.setLayout(flo)
            
            d.exec_()
        self.pet_view.clicked.connect(name_pet)
        
        self.layout.addWidget(self.pet_view)
        
        
    def update_renderPet2(self):
        # clear all icon images
        self.model.clear()
        for pet_entry in self.game.pet_objects:
            # update the icon
            self.model.appendRow(pet_entry.get_image())
            
    def game_event(self):
        [event_text,event_pet]=self.game.event()
        msg = QMessageBox()
        msg.setText(event_text)
        msg.setWindowTitle("Event")
        #msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        returnValue = msg.exec()
        if returnValue == QMessageBox.Ok:
            self.util.debug("OK clicked in game_event")
            self.game.createPet(event_pet)
        
class Util():
    
    def debug(self,to_print):
        print_str = str(to_print)
        debug_file=open(mw.pm.addonFolder()+"\\AnkiPet\\debug\\debugfile.txt","a")
        debug_file.write("\n"+print_str)
        debug_file.close()
        
    
