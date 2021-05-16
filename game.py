# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
#from aqt.utils import showInfo
# import all of the Qt GUI library
#from aqt.qt import *
# import the collection
#from anki import Collection
#from anki.consts import *
from anki.stats import CollectionStats
from anki.utils import  ids2str

import math
import json
import datetime 
import random

from . import pet

# saves to json only happen when progress_down_days is done, on pet creation, when the day is resolved and when exited.

class Game():

    def __init__(self):
        self.util = Util()
        self.config = mw.addonManager.getConfig("AnkiPet\\user_files\\")
        #{"lastResolve": "2021-05-15", "reputation": 68.75, "zeal": [0, 0, 6, 7, 7, 0, 7, 0, 0, 7, 6, 0, 0, 0, 0], "pets": ["Cat"], "age": [0], "names": ["Schatt"], "rep": [41.25], "events": [1, 0]}
        try:
            self.reputation = self.config['reputation']
            self.lastResolve = self.config['lastResolve']
            self.zeal = self.config['zeal']
            
            self.petList = self.config['pets']
            self.ageList = self.config['age']
            self.max_ageList = self.config['max_age']
            self.nameList = self.config['names']
            self.repList = self.config['rep']
            self.eventsList = self.config['events']
            self.util.debug("\tGame __init__ config values: "+str(self.config))
        except:
            self.util.debug("\tGame __init__: didn't find config or error in assigning values.")
            self.reputation = 0
            date_resolve = datetime.date.today()-datetime.timedelta(days=1)
            self.lastResolve = date_resolve.isoformat()
            self.zeal = [0]*15
            self.petList = []
            self.ageList = []
            self.max_ageList = []
            self.nameList = []
            self.repList = []
            self.eventsList = []
        self.tokens=0
        self.pet_objects=[]
        self.firstAnimal = False
        self.stable_mood = ':)'
        # then load the pet list into pet_objects
        self.load_pets()
        self.util.debug("\tGame __init__: loaded the pets.")
        # first load the pets into a list and process the days without updates
        self.progress_down_days()
        self.util.debug("\tGame __init__: progressed down days.")
        
    # this method should be split up into individual methods
    def getTodayStats(self):
        # need the collection
        col = mw.col
        
        # cards that are due or done:
        to_do_recent = 0
        to_do_all = 0
        done_today = 0
        
        # col.crt    creation time of the collection in seconds - due is given relative to this in days
        # due        for not new or not learning this is due in relation to crt in days
        coll_crt = col.db.all("select crt from col ")
        
        coll_crt_date = datetime.datetime.fromtimestamp(coll_crt[0][0])
        crt_to_today = datetime.datetime.now()-coll_crt_date
        days_crt_to_today = crt_to_today.days
        
        # cards that are due and in type=review and queue=review
        cards_due_type = col.db.all("select count(*) from cards where due <= %s and type=2 and queue=2" % days_crt_to_today)
        to_do_all = cards_due_type[0][0]
        self.util.debug("\tGame getTodayStats: due until today "+str(to_do_all))
        
        # only cards that became due in the last days
        cards_due_type = col.db.all("select count(*) from cards where %s < due and due <= %s and type=2 and queue=2" % (days_crt_to_today-3,days_crt_to_today))
        to_do_recent = cards_due_type[0][0]
        self.util.debug("\tGame getTodayStats: due today "+str(to_do_recent))
            
        # done today
        # done contains (day, learn, yound, mature) list
        done= col.db.all("""
    select
    (cast((id/1000.0 - :cut) / 86400.0 as int))/:chunk as day,
    sum(case when type = 0 then 1 else 0 end), -- lrn count
    sum(case when type = 1 and lastIvl < 21 then 1 else 0 end), -- yng count
    sum(case when type = 1 and lastIvl >= 21 then 1 else 0 end) -- mtr count
    from revlog %s
    group by day order by day""" % "",
                                cut=col.sched.dayCutoff,
                                tf=3600.0,
                                chunk=1)
        if done[-1][0]==0:
            done_today = sum(done[-1])
        else:
            done_today = 0
        self.util.debug("\tGame getTodayStats: done today "+str(done_today))
        
        return [to_do_recent,done_today,done_today/float(to_do_recent+done_today),self.tokens,self.reputation]

    
    def check_excecution_date(self):
        # check that not today date and check for case where resolve is done after midnight to 4 oclock
        # in the midnight to 4 case change the lastResolve date to day before
        # case days == 2 and it is between 0 and 4 hours -> allowed and day counts as previous day
        # case days == 1 and it is between 0 and 4 hours -> forbidden, counts as same day
        do_resolve=False       # case when self.lastResolve==today
        lastResolve=''
        if self.lastResolve != str(datetime.date.today()):  # check if it is past midnight to 4 and lastResolve was on previous day
            days_str = datetime.date.today()-datetime.datetime.strptime(self.lastResolve, '%Y-%m-%d').date()
            days=days_str.days
            if days > 1:
                do_resolve=True
                lastResolve = datetime.date.today()
                if days == 2:
                    date_hour = datetime.datetime.now().hour
                    if date_hour < 4:
                        lastResolve = datetime.date.today()-datetime.timedelta(1)
            if days == 1:
                date_hour = datetime.datetime.now().hour
                if date_hour >= 4:
                    do_resolve=True
                    lastResolve = datetime.date.today()
        return [do_resolve,lastResolve]

    
    def resolveDay(self):
        # to only excecute once per day:
        [resolve,date_lastResolve]=self.check_excecution_date()
        self.util.debug(str([resolve,date_lastResolve]))
        if resolve:
            # check if last resolve is more than one day in the past:
            self.progress_down_days()                                            
            # get new tokens from days stats
            stats = self.getTodayStats()
            frac=stats[2]*100
            tok=int(math.sqrt(frac))
            self.tokens+=tok
            # optionally - get reputation
            rep_factor=0
            if len(self.zeal)==15:
                averageZeal = sum(self.zeal)/float(15)
                if averageZeal > 9.8:                            # at max one 8 or two 9 in last 15 days
                    rep_factor=1
                elif averageZeal > 9:
                    rep_factor=0.75
                elif averageZeal > 8:
                    rep_factor=0.5
            if rep_factor > 0:
                for idx,pet in enumerate(self.pet_objects):
                    pet_rep_inc=pet.rep_max*rep_factor
                    pet.rep+=pet_rep_inc
                    self.reputation+=pet_rep_inc
            self.zeal.append(tok)
            self.zeal.pop(0)
            
            self.progressPets(self.tokens)
            self.lastResolve = str(date_lastResolve)
            
            self.save_pets()
        else:
            pass

    def factor(self,tokens):
        if tokens == 10:
            return 1
        elif tokens == 9:
            return 1/1.5
        elif tokens == 8:
            return 1/2.0
        elif tokens == 7:
            return 1/3.0
        elif tokens == 6:
            return 1/3.0
        elif tokens == 5:
            return 0.0
        elif tokens == 4:
            return -1/3.0
        elif tokens == 3:
            return -1/3.0
        elif tokens == 2:
            return -1/2.0
        elif tokens == 1:
            return -1/1.5
        elif tokens == 0:
            return -1/1.5

            
    #################################################################################
    ##### Pet objects manipulation methods ##########################################
    #################################################################################            
            
            
    def progressPets(self,tokens):
        #days = datetime.date.today()-datetime.datetime.strptime(self.lastResolve, '%Y-%m-%d').date()
        progress = self.factor(tokens)
        for pet_entry in self.pet_objects:
            pet_entry.age+=progress
        self.tokens = 0
        self.check_death_oldAge()
        
    def createPet(self,id_str):
        '''creates a single new pet and stores it in pet list and json file'''
        max_age = pet.get_max_age(id_str)
        new_pet = self.create_pet_object(id_str,age=0,max_age=max_age,name='',rep=0)
        self.pet_objects.insert(0,new_pet)
        if self.reputation >= 100:                      # so that the first pet doesn't cause the reput. to go negative
            self.reputation = self.reputation-100 
        self.save_pets()
        
        
    def petDies(self,idx):
        del self.pet_objects[idx]
        # put here: if len(pet_objects)==1 and pet has 0 age after delete then restart the game with a single egg
        # put here: code for a cemetary
        
    
    def check_death_oldAge(self):
        for idx,pet_entry in enumerate(self.pet_objects):
            if pet_entry.age > pet_entry.max_age:
                self.petDies(idx)
        
        
    def create_pet_object(self,id_str,age=0,max_age=1000,name='',rep=0):
        if id_str == "Chicken":
            self.util.debug("\t\t\tCreating a chicken.")
            pet_obj=pet.Chicken(age,max_age,name,rep)
        elif id_str == "Cat":
            self.util.debug("\t\t\tCreating a cat.")
            pet_obj=pet.Cat(age,max_age,name,rep)
        self.util.debug("\t\t\tGame create_pet_object: "+pet_obj.pet_string())
        return pet_obj
        
    def load_pets(self):
        '''load the pets from the petList into pet objects '''
        if self.petList == []:
            self.firstAnimal = True
        for idx,pet_entry in enumerate(self.petList):
            self.util.debug("\t\tGame load_pets(): idx, pet_entry "+str(idx)+", "+str(pet_entry))
            # check the age of every pet before creating it!
            if self.ageList[idx] < 0:
                self.ageList[idx]=0
            try:
                name = self.nameList[idx]                            
            except:
                name = ''
            self.pet_objects.append(self.create_pet_object(pet_entry,age=float(self.ageList[idx]),max_age=self.max_ageList[idx],name=name,rep=self.repList[idx]))
            self.util.debug("\t\tGame load_pets() number of pets in pet_objects: "+str(len(self.pet_objects)))
           
    def save_pets(self):
        '''saves the pets and other information from the pet_objects list to the json file'''
        petList,ageList,max_ageList,nameList,repList = [],[],[],[],[]
        for idx,pet_entry in enumerate(self.pet_objects):
            petList.append(pet_entry.type)
            ageList.append(pet_entry.age)
            max_ageList.append(pet_entry.max_age)
            nameList.append(pet_entry.name)
            repList.append(pet_entry.rep)
        save={"lastResolve":self.lastResolve,"reputation":self.reputation,"zeal":self.zeal,"pets":petList, "age":ageList, "max_age":max_ageList, "names":nameList, "rep":repList, "events":self.eventsList}
        path=mw.pm.addonFolder()+"\\AnkiPet\\user_files\\config.json"
        with open(path, "w", encoding="utf8") as f:
            json.dump(save, f)
        self.util.debug("\t\tGame save_pets(): saved the pets to json file ")
    
    ##################################################################################
    ##################################################################################
    ##################################################################################
    
    def progress_down_days(self):
        '''on init - progress the days the game was not played   '''
        #days = datetime.date.today()#-datetime.datetime.strptime(self.lastResolve, '%Y-%m-%d').date()
        self.util.debug("\t\t\tGame progress_down_days(): start")
        try:
            days_str = datetime.date.today()-datetime.datetime.strptime(self.lastResolve, '%Y-%m-%d').date()
            self.util.debug("\t\t\tGame progress_down_days(): days_str "+str(days_str))
            days=days_str.days
            if days == 2:    # this checks for cases where the game is played after midnight to 4 oclock
                date_past_to_future = datetime.datetime.strptime(self.lastResolve, '%Y-%m-%d').date()+datetime.timedelta(2)      # add two days
                future = datetime.datetime.combine(date_past_to_future,  datetime.time(4, 0))                                      # 4oclock in the morning is added
                if datetime.datetime.now()<future:
                    days=1
        except:
            days = 0
        self.util.debug("\t\t\tGame progress_down_days(): days "+str(days))
        
        # for every day not played a zeal entry of 0 is added and progressed
        if days > 1: 
            days_count = days-1
            
            for day in range(days_count):
                self.zeal.append(0)
                self.zeal.pop(0)
                self.progressPets(0)
            
            date = datetime.date.today()- datetime.timedelta(days=1)   # set it to the previous day so that repetition doesn't do anything 
            self.lastResolve=str(date)                                 ###################### needs to be adapted to 4h rule
            self.save_pets()
            self.util.debug("\t\t\tGame progress_down_days(): zeal changed "+str(self.zeal))
        else:
            pass
        
        # check if pets die from neglection (no print to json here otherwise a pet would die on each game start)
        if sum(self.zeal) < 70:
            self.stable_mood = ':|'
        elif sum(self.zeal)<21:
            self.stable_mood = ':('
            if len(self.pet_objects)>1:
                self.petDies(-1)
                self.util.debug("\t\t\tGame progress_down_days(): a pet dies")
            else:
                try:
                    self.pet_objects[0].age=0
                except:
                    pass

                
    def name_this_pet(self,text,index):
        self.pet_objects[index].name=text
        

    def check_for_game_event(self):
        self.util.debug("Checking on game event")
        if self.reputation >= 100:         
            return True
        elif self.firstAnimal == True:
            return True
        else:
            return False
            
            
        # check all pets how many reached rep 100 -> wenn der wert = anzahl pets ist gibt es ein event
        # events in einer liste (pregnant cat, kitten or egg, plant or kitten, plant or goat,farm,breeding,...)
        # implement as qdialog with one or two buttons for the options
        
        # returns true or false  or event parameters
        
    def event(self):
        self.util.debug("Randomly choosing game event")
        #pick radom event which is not yet in events list
        offers_all=[]
        with open(mw.pm.addonFolder()+"\\AnkiPet\\pet_offers.txt") as pet_offers:
            for line in pet_offers:
                offers_all.append(line)
        offers_max = len(offers_all)
        #self.util.debug("Offers file: "+str(offers_all))
        #self.util.debug("Legth of pet offers file: "+str(offers_max))
        rand_event =  int(random.random()*1000)%offers_max 
        catch = 1
        while (rand_event in self.eventsList) and (catch < 100):
            rand_event =  int(random.random()*1000)%offers_max 
            catch+=1
        self.util.debug("Catch: "+str(catch))
        self.eventsList.append(rand_event)  
        self.util.debug("Random value: "+str(rand_event))
        # find the event
        #self.util.debug("Event string: "+offers_all[rand_event])
        #self.util.debug("Split: "+str(offers_all[rand_event].split("\t")))
        event_text=offers_all[rand_event].split("\t")[0]
        event_pet=offers_all[rand_event].split("\t")[1].split(".")[0]
        self.util.debug(event_text+", "+event_pet)
        return [event_text,event_pet]
            




class Util():
    
    def debug(self,to_print):
        print_str = str(to_print)
        debug_file=open(mw.pm.addonFolder()+"\\AnkiPet\\debug\\debugfile.txt","a")
        debug_file.write("\n"+print_str)
        debug_file.close()
        