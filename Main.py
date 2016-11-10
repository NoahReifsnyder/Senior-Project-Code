#Noah Reifsnyder
#Rachel Santangelo
#Senior Project 2016


# ------------------------------------------------------------------------------------------------
# Copyright (c) 2016 Microsoft Corporation
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------------------------

# Import our modules #####################################################################
import getXML
import GC
from Entity import Entity #basically just a set of local variables for position of AI, player, or a mob.
import Follow
##########################################################################################

import MalmoPython
import os
import signal
import sys
import time
import json
import math
from datetime import datetime


from collections import namedtuple


def end():
    print "Mission Ended"
    output=""
    if role==0:
        for x in range (h):
            output+=(str(learning[x][0])+","+str(learning[x][1])+"\n")
        print output
        table.write(output)
    
    table.close()
    exit(0)

def signal_handler(signal, frame):
    print "\nMission Interrupted"
    end()

signal.signal(signal.SIGINT, signal_handler)



EntityInfo = namedtuple('EntityInfo', 'x, y, z, name, quantity')
EntityInfo.__new__.__defaults__ = (0, 0, 0, "", 0)
pEntity = Entity( 0, 0, 0)
AI = Entity( 0, 0, 0)
AI.move=0
AI.flag=-1
AI.yaw=0
moblist=[]
table=open("LearningTable.txt" ,"w+")
w,h=2,11
learning=[[y for x in range(w)] for y in range(h)]
input=table.readline()
    #if input=="":
if input=="":
    for x in range(h):
        learning[x][0]=x+5
        learning[x][1]=0
else:
    x=0
    while(input!=""):
        a=input.split(",")
        learning[x][0]=a[0]
        learning[x][1]=a[1]
        x=x+1
print learning




def compare (mob, mob2):
    if distToEnt(mob, pEntity)<distToEnt(mob2, pEntity):
        return -1
    else:
        return 1
    return 0

def distToEnt(entity, entity2):
    dx=entity.x-entity2.x
    dz=entity.z-entity2.z
    return (dx**2+dz**2)**.5

def found_Entity(entity):
    agent_host.sendCommand("Move 0")
    yaw=(getYaw(entity))
    relYaw=getRelYaw(yaw)
    aRelYaw=math.fabs(relYaw)
    if (aRelYaw>5):
        turn(yaw)
    return


def getYaw(entity):
    dx=entity.x-AI.x
    dz=entity.z-AI.z
    a=0
    if(dz!=0):
        a=math.atan(dx/dz)*180/math.pi
    elif(dx<0):
        a=-90
    elif(dx>0):
        a=90
    if (dz<0):
        if (dx<0):
            a=a - 180
        else:
            a=a +180
    a=-1*a
    
    return a

def getRelYaw(yaw):
    dyaw=(yaw+180)-(AI.yaw+180)
    if(math.fabs(dyaw)>180):
        if(dyaw>0):
            return 360-dyaw
        else:
            return 360+dyaw
    return dyaw

def turn(yaw):
    relYaw=getRelYaw(yaw)
    velocity = 1
    if(relYaw<0):
        velocity=-1
    newVel=velocity
    c=0
    agent_host.sendCommand("turn "+str(velocity))
    if(relYaw>0):
        while(relYaw>0):
            if(newVel!=velocity):
                velocity=newVel
                agent_host.sendCommand("turn "+str(velocity))
            world_state = agent_host.getWorldState()
            if world_state.number_of_observations_since_last_state > 0:
                msg = world_state.observations[-1].text
                ob = json.loads(msg)
                if "Yaw" in ob:
                    AI.yaw = ob[u'Yaw']
                    relYaw=getRelYaw(yaw)
                    aRelYaw=math.fabs(relYaw)
                    if(aRelYaw<45):
                        newVel=relYaw/45
    else:
        while(relYaw<0):
            if(newVel!=velocity):
                velocity=newVel
                agent_host.sendCommand("turn "+str(velocity))
            world_state = agent_host.getWorldState()
            if world_state.number_of_observations_since_last_state > 0:
                msg = world_state.observations[-1].text
                ob = json.loads(msg)
                if "Yaw" in ob:
                    AI.yaw = ob[u'Yaw']
                    relYaw=getRelYaw(yaw)
                    aRelYaw=math.fabs(relYaw)
                    if(aRelYaw<45):
                        newVel=relYaw/45

    agent_host.sendCommand("turn 0")
    
def find_Entity(grid, entity):
    
    simple_grid = [[simplify_grid(grid, x, z) for x in range(-10, 10)] for z in range(-10, 10)]
    yaw=getYaw(entity)
    turn(yaw)
    
    #take the one dimensional grid ordered x by z and then by y value and create a 2D array from it
    #if the player can walk there, we want a 1 and if player can't walk there we want a 0
    #player will be at 0,0

    #set goal coordinate
    goalx=entity.x-AI.x
    goalz=entity.z-AI.z
    #simple_grid[int(pEntity.x)][int(pEntity.z)] = 3 This line broke code. Because moving and not updating.
    return 1#Follow.A_star_search(goalx, goalz, simple_grid)


def simplify_grid(grid, x, z):
    #check in front
    if grid[get_grid_coordinate(x, z, -1, 10)] != "water" and grid[get_grid_coordinate(x, z, -1, 10)] != "air" and grid[get_grid_coordinate(x, z, -1, 10)] != "lava":
        #check height in clear
        if grid[get_grid_coordinate(x, z, 0, 10)] == "air" and grid[get_grid_coordinate(x, z, 1, 10)] == "air":
                return 1
    return 0


def get_grid_coordinate(x, z, y, pos):
    #pos: max x and z dimensions in positive direction
    dim = pos * 2 + 1
    #adjust for negative values
    y += 1
    x += 10
    z += 10

    #convert 3d coordinates to 1D array coordinates and return value
    return x + z * dim + y * (dim * dim)


def lost_player():
    print("lost")
    return



# Create default Malmo objects:

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
agent_host = MalmoPython.AgentHost()
agent_host.addOptionalIntArgument( "role,r", "For multi-agent missions, the role of this agent instance", 0)
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print 'ERROR:', e
    print agent_host.getUsage()
    exit(1)
if agent_host.receivedArgument("help"):
    print agent_host.getUsage()
    exit(0)

role = agent_host.getIntArgument("role")
print "Will run as role", role

agent_host.setObservationsPolicy(MalmoPython.ObservationsPolicy.LATEST_OBSERVATION_ONLY)

# Create a client pool here - this assumes two local mods with default ports,
# but you could have two mods on different machines, and specify their IP address here.
client_pool = MalmoPython.ClientPool()
client_pool.add( MalmoPython.ClientInfo("127.0.0.1", 10000))
client_pool.add( MalmoPython.ClientInfo("127.0.0.1", 10001))

chat_frequency = 30 # if we send chat messages too frequently the agent will be disconnected for spamming
num_steps_since_last_chat = 0

my_mission = MalmoPython.MissionSpec(getXML.missionXML, True) #This loads the xml file, you could change True to variable to make sure the instance is valid before loading
my_mission_record = MalmoPython.MissionRecordSpec()
unique_experiment_id = ""#if you want to record unique instances of the expirement
# Attempt to start a mission:
max_retries = 3

#For loop here connects into the unique ports depending on the role assigned.
for retry in range(max_retries):
    try:
        agent_host.startMission( my_mission, client_pool, my_mission_record, role, unique_experiment_id)
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print "Error starting mission:",e
            exit(1)
        else:
            time.sleep(2)



# Loop until mission starts:
print "Waiting for the mission to start ",
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    sys.stdout.write(".")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print "Error:",error.text

print
print "Mission running ",
#Enter some hard coded commands in here


# Loop until mission ends:
if role == 0:
    time.sleep(2)
    plan = None
    AI.yaw=0
    attacking=False
    AI.flag=-1
    target=AI
    distance=10
    idCount=0
    while world_state.is_mission_running:
        world_state = agent_host.getWorldState()
        if world_state.number_of_observations_since_last_state > 0:
            msg = world_state.observations[-1].text
            ob = json.loads(msg)
            if "Player" in ob:
                if AI.flag==3 or AI.flag==4:
                    distance=20
                else:
                    distance=10
                AI.flag=-1
                target=AI
            if "Yaw" in ob:
                AI.yaw = ob[u'Yaw']
        

            if "Player" in ob:
                entities = [EntityInfo(**k) for k in ob["Player"]]
                for ent in entities:
                    if ent.name == "Typhoonizm":
                        AI.flag = 1
                        pEntity.x = ent.x
                        pEntity.y = ent.y
                        pEntity.z = ent.z

            
            if "Mob" in ob:
                entities = [EntityInfo(**k) for k in ob["Mob"]]
                count=0
                for mob in moblist:
                    mob.seen=False
                    mob.new=False
                for ent in entities:
                    if ent.name == "Zombie":
                        count=count+1
                        mob=Entity(ent.x,ent.y,ent.z)
                        inList=False
                        loc=5
                        for entity in moblist:
                             if not entity.new:
                                if(distToEnt(mob,entity)<loc):
                                    inList=True
                                    mob.id=entity.id
                                    loc=distToEnt(mob,entity)
                        if inList:
                            for entity in moblist:
                                if(mob.id==entity.id):
                                    entity.x=mob.x
                                    entity.z=mob.z
                                    entity.y=mob.y
                                    entity.seen=True
                        else:
                            mob.id=idCount
                            idCount=idCount+1
                            mob.seen=True
                            mob.new=True
                            moblist.append(mob)
                        if(distToEnt(mob,pEntity)<distance):
                            distance=distToEnt(mob, pEntity)
                            target=mob
                            AI.flag=3
                moblist=[ent for ent in moblist if ent.seen]
            
            if "Nearby" in ob:
                entities = [EntityInfo(**k) for k in ob["Nearby"]]
                AI.x = entities[0].x
                AI.y = entities[0].y
                AI.z = entities[0].z
                for ent in entities:
                    if ent.name == "Typhoonizm" and target==AI:
                        AI.flag = 2
                        pEntity.x = ent.x
                        pEntity.y = ent.y
                        pEntity.z = ent.z
                    elif ent.name == "Zombie":
                        agent_host.sendCommand("attack 1") #for when zombies in way of target
                        if target.x == ent.x and target.z==ent.z:
                            AI.flag = 4
                            
            if AI.flag==1 and attacking:
                agent_host.sendCommand("attack 0")
                attacking=False

            if AI.flag == -1:
                lost_player()
            elif AI.flag == 1:
                yaw=getYaw(pEntity)
                relYaw=getRelYaw(yaw)
                aRelYaw=math.fabs(relYaw)
                if(aRelYaw>5):
                    turn(yaw)
                    agent_host.sendCommand("Move 1")
                    find_Entity(ob.get(u'floorGrid', 0), pEntity)
                else:
                    agent_host.sendCommand("Move 1")
                #plan.reverse()
                #agent_host.sendCommand(plan.pop())

            elif AI.flag == 2:
                found_Entity(pEntity)
            elif AI.flag == 3:
                yaw=getYaw(target)
                relYaw=getRelYaw(yaw)
                aRelYaw=math.fabs(relYaw)
                if(aRelYaw>10):
                    turn(yaw)
                    agent_host.sendCommand("Move 1")
                    find_Entity(ob.get(u'floorGrid', 0), target)
                else:
                    agent_host.sendCommand("Move 1")
            elif AI.flag == 4:
                agent_host.sendCommand("attack 1")
                attacking=True
                found_Entity(target)

            moblist.sort(compare)
            if count>0:
                print count
            for mob in moblist:
                print str(mob.id)+" "+str(distToEnt(mob, pEntity))
            print "\n\n\n\n"




else:
    while world_state.is_mission_running:
        sys.stdout.write(".")
        time.sleep(20)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print "Error:",error.text
end()


# Mission has ended.
