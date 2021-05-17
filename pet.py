# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *
# import the collection
#from anki import Collection
#from anki.utils import ids2str
import math
#import json
import random,os


def get_max_age(id_str):
    age_dict_lower = {'Chicken':700, 'Cat':1000}
    age_dict_upper = {'Chicken':1500, 'Cat':20000}
    return random.randint(age_dict_lower[id_str],age_dict_upper[id_str])

PATH = os.path.abspath(os.path.dirname(__file__))


class Pet():
    def __init__(self,type,age=0,max_age=1000,name='',rep=0):
        self.age=age                             # age starts with 0
        self.max_age=max_age
        self.type=type
        self.name=str(name)
        self.rep=rep
        
    def pet_string(self):
        return("Type: "+str(self.type)+", age: "+str(self.age)+", name: "+str(self.name)+", rep: "+str(self.rep))
        
    def get_item(self,filename,pic_slot):
        item = QStandardItem()
        pix = QPixmap(filename)
        rect = QRect(0+500*pic_slot, 0, 500, 500)                                # x,y,width,height
        cropped = pix.copy(rect)
        graph=QIcon(cropped)
        item.setIcon(graph)
        item.setText("Species: "+self.type+"\nName: "+self.name+" \nAge: "+str(math.floor(self.age))+" days")
        return item
        
    def debug(self,to_print):
        print_str = str(to_print)
        debug_file=open(os.path.join(PATH,"debug\\debugfile.txt"),"a")
        debug_file.write("\n\tPet: "+print_str)
        debug_file.close()
        
        
        
        
class Chicken(Pet):
   
    def __init__(self,age=0,max_age=1000,name='',rep=0):
        super().__init__("Chicken",age,max_age,name,rep)
        self.rep_max=2

    def pic_slot(self):
        pic_slot=0
        factor=0
        if self.age < 20:                                                           # going from 0 to 19 (20 pics)
            filename = "graphics\\Egg.png" #mw.pm.addonFolder()+"\\AnkiPet\\graphics\\Egg.png"
            pic_slot = int(math.floor(self.age))
        if self.age > 20 and self.age < 40:
            filename = "graphics\\Chick.png" #mw.pm.addonFolder()+"\\AnkiPet\\graphics\\Chick.png"      # 20 chick pics
            pic_slot = int(math.floor(self.age)-20)
        if self.age >= 40:
            filename = "graphics\\Chicken.png" #mw.pm.addonFolder()+"\\AnkiPet\\graphics\\Chicken.png"      # 20 chicken pics
            if self.age < 72:
                factor = math.floor(int(math.floor(self.age)-40)/6)
                pic_slot = int(math.floor(self.age)-40)%2+factor*2
            if self.age >= 72:
                pic_slot = random.randrange(12,20)
        return [pic_slot, filename]
    
    def get_image(self):
        super().debug("Fetching chicken pic")
        [pic_slot,filename]= self.pic_slot()
        super().debug("Pic slot: "+str(pic_slot))
        return super().get_item(os.path.join(PATH,filename),pic_slot)

        
class Cat(Pet):
    
    def __init__(self,age=0,max_age=1000,name='',rep=0):
        super().__init__("Cat",age,max_age,name,rep)
        self.rep_max=3
    
    def pic_slot(self):
        pic_slot=0
        factor=0
        if self.age < 20:                                                           # going from 0 to 19 (20 pics)
            filename = "graphics\\kitten_series1to20.png" #mw.pm.addonFolder()+"\\AnkiPet\\graphics\\kitten_series1to20.png"
            pic_slot = int(math.floor(self.age))
        if self.age > 20 and self.age < 40:
            filename = "graphics\\kitten_series1to20.png"  #mw.pm.addonFolder()+"\\AnkiPet\\graphics\\kitten_series1to20.png"      
            pic_slot = int(math.floor(self.age)-20)
        if self.age >= 40:
            filename = "graphics\\kitten_series1to20.png"  #mw.pm.addonFolder()+"\\AnkiPet\\graphics\\kitten_series1to20.png"      
            if self.age < 72:
                factor = math.floor(int(math.floor(self.age)-40)/6)
                pic_slot = int(math.floor(self.age)-40)%2+factor*2
            if self.age >= 72:
                pic_slot = random.randrange(12,20)
        return [pic_slot, filename]
        
    def get_image(self):
        super().debug("Fetching cat pic")
        [pic_slot,filename]= self.pic_slot()
        super().debug("Pic slot: "+str(pic_slot))
        return super().get_item(os.path.join(PATH,filename),pic_slot)
        

        
        
        
        