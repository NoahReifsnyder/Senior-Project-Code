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
import sys
import time
import json
import math
from datetime import datetime


from collections import namedtuple
EntityInfo = namedtuple('EntityInfo', 'x, y, z, name')
EntityInfo.__new__.__defaults__ = (0, 0, 0, "")

pEntity = Entity(0, 0, 0, 0)
AI = Entity(0, 0, 0, 0)
del AI.flag
AI.yaw=0



def found_player():
    agent_host.sendCommand("Jump 1")
    print("found")
    return


def getYaw():
    dx=pEntity.x-AI.x
    dz=pEntity.z-AI.z
    a=0
    if(dz!=0):
        a=math.atan(dx/dz)*180/math.pi
    elif(dx<0):
        a=-90
    elif(dx>0):
        a=90
    a=-1*a
    return a

def turn(yaw):
    velocity = 1
    dyaw=(AI.yaw+180)-(yaw+180)
    while(dyaw**2>.05):
        agent_host.sendCommand("turn "+str(velocity))
        while(dyaw<0):
            #print AI.yaw
            world_state = agent_host.getWorldState()
            if world_state.number_of_observations_since_last_state > 0:
                msg = world_state.observations[-1].text
                ob = json.loads(msg)
                if "Yaw" in ob:
                    AI.yaw = ob[u'Yaw']
                    dyaw=(AI.yaw+180)-(yaw+180)
        velocity=float(velocity)/(-2)
        agent_host.sendCommand("turn "+str(velocity))
        while(dyaw>0):
            #print AI.yaw
            world_state = agent_host.getWorldState()
            if world_state.number_of_observations_since_last_state > 0:
                msg = world_state.observations[-1].text
                ob = json.loads(msg)
                if "Yaw" in ob:
                    AI.yaw = ob[u'Yaw']
                    dyaw=(AI.yaw+180)-(yaw+180)
        
        agent_host.sendCommand("turn 0")
        velocity=float(velocity)/(-2)
    print str(dyaw)+" "+str(AI.yaw)+" "+str(yaw)
    
def find_player(grid):
    
    simple_grid = [[simplify_grid(grid, x, z) for x in range(-10, 10)] for z in range(-10, 10)]
    yaw=getYaw()
    turn(yaw)
    ctime=datetime.now().second
    
    #take the one dimensional grid ordered x by z and then by y value and create a 2D array from it
    #if the player can walk there, we want a 1 and if player can't walk there we want a 0
    #player will be at 0,0

    #set goal coordinate
    goalx=pEntity.x-AI.x
    goalz=pEntity.z-AI.z
    simple_grid[int(pEntity.x)][int(pEntity.z)] = 3
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
    plan = None
    while world_state.is_mission_running:
        GC.pFlag = 0
        world_state = agent_host.getWorldState()
        if world_state.number_of_observations_since_last_state > 0:
            msg = world_state.observations[-1].text
            ob = json.loads(msg)
            if "Yaw" in ob:
                AI.yaw = ob[u'Yaw']
            if "Nearby" in ob:
                entities = [EntityInfo(**k) for k in ob["Nearby"]]
                AI.x = entities[0].x
                AI.y = entities[0].y
                AI.z = entities[0].z
                for ent in entities:
                    if ent.name == "Typhoonizm":
                        pEntity.flag = 2
                        pEntity.x = ent.x
                        pEntity.y = ent.y
                        pEntity.z = ent.z
        

            if "Player" in ob:
                entities = [EntityInfo(**k) for k in ob["Player"]]
                for ent in entities:

                    if ent.name == "Typhoonizm":
                        pEntity.flag = 1
                        pEntity.x = ent.x
                        pEntity.y = ent.y
                        pEntity.z = ent.z

            if pEntity.flag == 0:
                lost_player()
            elif pEntity.flag == 1:
                find_player(ob.get(u'floorGrid', 0))
                #plan.reverse()
                #agent_host.sendCommand(plan.pop())
            elif pEntity.flag == 2:
                found_player()


else:
    while world_state.is_mission_running:
        sys.stdout.write(".")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print "Error:",error.text
print "Mission ended"
# Mission has ended.
