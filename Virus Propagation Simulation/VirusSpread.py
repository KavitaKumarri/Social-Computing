#!/usr/bin/env python
# coding: utf-8

# In[1]:


from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from enum import IntEnum
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# In[2]:


class VirusState(IntEnum):
    NonInfected = 0,
    InfectedAsymtomatic = 1,
    InfectedSymptomatic = 2,
    Critical = 3,
    Cured = 4,
    Deceased = 5


PossiblePlacesList = ["Home","GroceryStore","Park","Quarantine"] 

class Park(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id,model)
        self.infectedAgent =0
        self.agentCount =0
    
    def addAgentInPark(self):
        self.agentCount+=1
        if self.state is VirusState.Infected:
            self.infectedAgent+=1
    
    def getAgentsInPark(self):
        parkAgents=[]
        for agent in model.schedule.agents:
            if agent.place == PossiblePlacesList[2] and agent.placeId == self.unique_id:
                parkAgents.append(agent)
       # print(len(parkAgents))
        return parkAgents
               
    
class GroceryStore(Agent):
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        self.agentCount = 0
        self.infectedCount = 0
        
    def addAgentInGroceryStore(self,state):
        self.agentCount+=1
        if state is VirusState.Infected:
            self.infectedAgent+=1
    
    def getAgentsInGroceryStore(self):
        groceryAgents = []
        for agent in model.schedule.agents:
            if agent.place == PossiblePlacesList[1] and agent.placeId == self.unique_id:
                groceryAgents.append(agent)
        return groceryAgents
            
            

class Home(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
    
    def getFamily(self):
        family = []
        for agent in model.schedule.agents:
            if agent.place == PossiblePlacesList[0] and agent.placeId == self.unique_id:
                family.append(agent)
        return family
        
        
    def homeInfected(self):
        pass

        

class QuarantineCenter(Agent):
    def __init__(self,unique_id, model,quarantineCapacity):
        super().__init__(unique_id, model)
        self.bedCount = quarantineCapacity
        
    def addPatient(self):
        if self.bedCount == 0:
            return False
        else:
            self.bedCount-=1
            return True
            
    def removeAgent(self):
        self.bedCount+=1
 


# In[3]:


def infectionInPark():
    print()


# In[5]:


class PopulationAgent(Agent):
    def __init__(self, unique_id, model,placeId):
        super().__init__(unique_id, model)
        self.infection_time = 0
        self.state = VirusState.NonInfected
        self.place = PossiblePlacesList[0] #PossiblePlaces.Home
        self.placeId = placeId
        self.lockdown = False
        self.quarantine = False
        self.houseNumber = placeId
        #print(self.placeId)
    
    def spreadVirusAtPlace(self):
        agents=[]
        if self.place == PossiblePlacesList[0]:
            #print(self.placeId)
            agents = self.model.houses[self.placeId].getFamily()
            
        elif self.place == PossiblePlacesList[2]:
            #print(self.placeId)
            park = self.model.parks[self.placeId]
            agents = park.getAgentsInPark()
        
        elif self.place == PossiblePlacesList[1]:
            #print(self.placeId)
            agents = self.model.groceryStores[self.placeId].getAgentsInGroceryStore()
        
        for agent in agents:
            if agent.state == VirusState.NonInfected:
                if self.random.random() < self.model.infectionRate:
                    agent.state = VirusState.InfectedAsymtomatic
        
    #quaratine change
    def quaratineAgent(self):
        if self.model.quarantineCenter.addPatient():
            self.quarantine = True
            self.placeId = -1
            self.place = PossiblePlacesList[3]
    
    def changeAgentState(self):
        if self.state == VirusState.NonInfected:
            p = self.model.infectionRate
            newState = np.random.choice([0,1],p=[p,1-p])
            if newState == 1:
                self.state =  VirusState.InfectedAsymtomatic
                #self.quaratineAgent()
        elif self.state == VirusState.InfectedAsymtomatic:
            newState = np.random.choice([0,1],p=[0.75,0.25])
            if newState == 1:
                self.state = VirusState.InfectedSymptomatic
                prob = np.random.choice([0,1],p=[0.8,0.2])
                if prob == 1:
                    self.quaratineAgent()
            
        elif self.state == VirusState.InfectedSymptomatic:
            newState = np.random.choice([0,1,2],p=[0.15,0.10,0.75])
            if newState == 0:
                self.state = VirusState.Cured
                if self.quarantine == True:
                    self.model.quarantineCenter.removeAgent()
            if newState == 1:
                self.state = VirusState.Critical
                if self.quarantine == False:
                    self.quaratineAgent()
            else:
                if self.quarantine==False:
                    prob = np.random.choice([0,1],p=[0.8,0.2])
                    if prob == 1:
                        self.quaratineAgent()
                
        elif self.state == VirusState.Critical:
            newState = np.random.choice([0,1,2],p=[0.75,0.05,0.20])
            if newState == 2:
                self.state = VirusState.Deceased
                if self.quarantine == True:
                    self.model.quarantineCenter.removeAgent()
            elif newState == 1:
                self.state = VirusState.Cured
                if self.quarantine == True:
                    self.model.quarantineCenter.removeAgent()
            else:
                if self.quarantine==False:
                    self.quaratineAgent()
       # if self.quarantine==False and self.state in ( VirusState.InfectedAsymtomatic,VirusState.InfectedSymptomatic,VirusState.Critical)  :
       #     self.spreadVirusAtPlace()
        
            
        """ 
        if self.state in(VirusState.InfectedAsymtomatic, VirusState.Critical,VirusState.InfectedSymptomatic):
            if self.place == PossiblePlacesList[2]:
                parkInfectedCount+=1
            elif self.place == PossiblePlacesList[1]:
                groceryInfectedCount+=1
        """        
           # park[np.random.choice(0,1)].addAgent(self)    
    
 
    
    def mobilize(self):
        if self.quarantine==False and self.state in ( VirusState.InfectedAsymtomatic,VirusState.InfectedSymptomatic,VirusState.Critical)  :
            self.spreadVirusAtPlace()
        if self.place != PossiblePlacesList[0]:
            self.place = PossiblePlacesList[0]
            self.placeId = self.houseNumber
        else:
        
            choice = np.random.choice([0,1,2], p =[0.7,0.1,0.2])  #0=home, 1= park, 2 = grocery
            self.place = PossiblePlacesList[choice]
            if choice == 2:
                self.placeId = np.random.choice([0,1])
            elif choice == 1:
                self.placeId = np.random.choice([0,1,2,3,4])
         
        self.changeAgentState()   
      
    
    
    def changePlace(self):
        if  self.quarantine:
            self.changeAgentState()
        else:
            self.mobilize()
            
        """  if self.place == PossiblePlacesList[2]:
                parkAgentCount+=1
            if self.place == PossiblePlacesList[1]:
                groceryAgentCount+=1
                    
             """   
    
    def isInfectedAgent(self):
        if self.state == VirusState.NonInfected or self.state ==  VirusState.Cured or self.state ==  VirusState.Deceased:
            return False
        else:
            return True
    
    def step(self):
        if self.state is VirusState.Deceased: # or VirusState.Cured:
            return
        self.changePlace()
        #self.changeAgentState()
       # a = self.state
       # print("Agent " + str(self.unique_id) + "  " + self.place + "  " + str(a) + ".")


# In[6]:


def getTotalDeceasedCount(model):
    count = 0;
    for a in model.schedule.agents:
        if a.state is VirusState.Deceased:
            count+=1
    return count

def getTotalCuredCount(model):
    count = 0
    for a in model.schedule.agents:
        if a .state is VirusState.Cured:
            count+=1
    return count;

def getTotalInfectedCount(model):
    count = 0
    for a in model.schedule.agents:
        if a.state in( VirusState.InfectedAsymtomatic,VirusState.InfectedSymptomatic,VirusState.Critical):
            count+=1
    return count
   


# In[7]:


def getBedCount(model):
    return model.quarantineCapacity - model.quarantineCenter.bedCount


# In[8]:


class InfectionModel(Model):
    def __init__(self,population_size, infectedCount,quarantineCapacity,infectedRate, seed=None):
        self.AgentCount = population_size
        self.schedule = RandomActivation(self)
        self.agents=[]
        self.infectedCount = infectedCount
        self.infectionRate =infectedRate
        self.houses = []
        self.parks = []
        self.groceryStores = []
        self.currentrun = 0
        self.quarantineCapacity = quarantineCapacity
        self.quarantineCenter = QuarantineCenter(1,self,quarantineCapacity)
        #assign agents to housenumbers
        agentId=1
        for houseNumber in range(250):
            self.houses.append(Home(houseNumber,self))
            for house in range(4):
                agent = PopulationAgent(agentId,self,houseNumber)
                if self.random.random() < self.infectedCount:
                    agent.state = VirusState.InfectedAsymtomatic
                self.schedule.add(agent)
                agentId+=1
        
        for i in range(2):
            self.parks.append(Park(i,self))
        for i in range(5):
            self.groceryStores.append(GroceryStore(i,self))
            
    
        self.datacollector = DataCollector(
        model_reporters = {
            "totalInfected": getTotalInfectedCount,
            "Cured": getTotalCuredCount,
            "Deceased" : getTotalDeceasedCount,
            "BedCount" : getBedCount
        }
        )
    
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self.currentrun +=1


# In[10]:


populationSize = 1000
infectedCount = 0.10
cycles = 40
quarantineCapacity = 100
infectedRate = 0.05
model = InfectionModel(populationSize, infectedCount,quarantineCapacity,infectedRate)
currentrun = 0
runCount = cycles


while 1:
    model.step()
    if runCount > 0 and currentrun >= runCount:
        break
    currentrun += 1

modelData = model.datacollector.get_model_vars_dataframe()
modelData.plot()
plt.show()


# In[12]:


populationSize = 1000
infectedCount = 0.25
cycles = 40
quarantineCapacity = 100
infectedRate = 0.05
model = InfectionModel(populationSize, infectedCount,quarantineCapacity, infectedRate)
currentrun = 0
runCount = cycles


while 1:
    model.step()
    if runCount > 0 and currentrun >= runCount:
        break
    currentrun += 1

modelData = model.datacollector.get_model_vars_dataframe()

modelData.plot()
print(modelData)
plt.show()


# In[656]:


populationSize = 1000
infectedCount = 0.50
cycles = 40
quarantineCapacity = 100
infectedRate = 0.05
model = InfectionModel(populationSize, infectedCount,quarantineCapacity,infectedRate)
currentrun = 0
runCount = cycles


while 1:
    model.step()
    if runCount > 0 and currentrun >= runCount:
        break
    currentrun += 1

modelData = model.datacollector.get_model_vars_dataframe()
modelData.plot()
print(modelData)
plt.show()


# In[647]:


#Social Distancing with 10% population

populationSize = 1000
infectedCount = 0.10
cycles = 40
quarantineCapacity = 100
infectedRate = 0.01
model = InfectionModel(populationSize, infectedCount,quarantineCapacity,infectedRate)
currentrun = 0
runCount = cycles


while 1:
    model.step()
    if runCount > 0 and currentrun >= runCount:
        break
    currentrun += 1

modelData = model.datacollector.get_model_vars_dataframe()
modelData.plot()
print(modelData)
plt.show()


# In[662]:


#Social Distancing with 25% population

populationSize = 1000
infectedCount = 0.25
cycles = 40
quarantineCapacity = 100
infectedRate = 0.01
model = InfectionModel(populationSize, infectedCount,quarantineCapacity,infectedRate)
currentrun = 0
runCount = cycles


while 1:
    model.step()
    if runCount > 0 and currentrun >= runCount:
        break
    currentrun += 1

modelData = model.datacollector.get_model_vars_dataframe()
modelData.plot()
print(modelData)
plt.show()


# In[13]:


#Social Distancing with 50% population

populationSize = 1000
infectedCount = 0.50
cycles = 40
quarantineCapacity = 100
infectedRate = 0.01
model = InfectionModel(populationSize, infectedCount,quarantineCapacity,infectedRate)
currentrun = 0
runCount = cycles


while 1:
    model.step()
    if runCount > 0 and currentrun >= runCount:
        break
    currentrun += 1

modelData = model.datacollector.get_model_vars_dataframe()
modelData.plot()
print(modelData)
plt.show()


# In[650]:



populationSize = 1000
infectedCount = 0.10
cycles = 50
quarantineCapacity = 100
infectedRate = 0.05
model = InfectionModel(populationSize, infectedCount,quarantineCapacity,infectedRate)
currentrun = 0
runCount = cycles


while 1:
    model.step()
    if runCount > 0 and currentrun >= runCount:
        break
    currentrun += 1

modelData = model.datacollector.get_model_vars_dataframe()
modelData.plot()
print(modelData)
plt.show()


# In[573]:





# In[269]:




