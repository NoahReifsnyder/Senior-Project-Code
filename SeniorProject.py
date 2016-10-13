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

# Tutorial sample #2: Run simple mission using raw XML

import MalmoPython
import os
import sys
import time
import json
from collections import namedtuple
EntityInfo = namedtuple('EntityInfo', 'x, y, z, name')
EntityInfo.__new__.__defaults__ = (0, 0, 0, "")



def foundPlayer():
    agent_host.sendCommand("Jump 1")
    print("found")
    return
def lostPlayer():
    agent_host.sendCommand("Jump 0")
    print("lost")
    return





missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
              <About>
                <Summary>Hello world!</Summary>
              </About>
              <ServerSection>
                <ServerInitialConditions>
                    <Time>
                        <StartTime>18000</StartTime>
                        <AllowPassageOfTime>false</AllowPassageOfTime>
                        </Time>
                    <Weather>clear</Weather>
                </ServerInitialConditions>
                <ServerHandlers>
                    <FlatWorldGenerator generatorString="3;1*minecraft:bedrock,7*minecraft:dirt,1*minecraft:grass;2;"/>
                    <DrawingDecorator>
                        <DrawCuboid x1="1" y1="8" z1="1" x2="7" y2="12" z2="7" type="obsidian" />
                        <DrawCuboid x1="2" y1="9" z1="2" x2="6" y2="11" z2="6" type="air" />
                        
                        <DrawCuboid x1="1" y1="9" z1="4" x2="7" y2="10" z2="4" type="air" />
                        <DrawCuboid x1="7" y1="9" z1="4" x2="7" y2="10" z2="4" type="air" />
                        <DrawCuboid x1="4" y1="9" z1="1" x2="4" y2="10" z2="1" type="air" />
                        <DrawCuboid x1="4" y1="9" z1="7" x2="4" y2="10" z2="7" type="air" />
                        
                        <DrawBlock x="4" y="9" z="4" type="redstone_block" />
                        <DrawBlock x="4" y="8" z="4" type="air" />
                        <DrawBlock x="4" y="7" z="4" type="diamond_block" />
                        
                        <!--
                        <DrawBlock x="114" y="9" z="-9" type="mob_spawner" variant="Skeleton" />
                        <DrawBlock x="-119" y="9" z="4" type="mob_spawner" variant="Skeleton" />
                        <DrawBlock x="114" y="9" z="17" type="mob_spawner" variant="Zombie" />
                        <DrawBlock x="117" y="9" z="4" type="mob_spawner" variant="Zombie" />
                        -->
                    </DrawingDecorator>
                  <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
              </ServerSection> 
              
              <AgentSection mode="Survival">
              <Name>Burton</Name>
              <AgentStart>
              <Placement x="0.5" y="9.0" z="0.5"/>
              </AgentStart>
              <AgentHandlers>
              <ObservationFromChat />
                <ObservationFromNearbyEntities>
                <Range name="Nearby" xrange="2" yrange="2" zrange="2" />
                <Range name="Mob" xrange="10" yrange="2" zrange="10" update_frequency="100"/>
                <Range name="Player" xrange="100" yrange="2" zrange="100" update_frequency="100"/>
              </ObservationFromNearbyEntities>
              <ContinuousMovementCommands turnSpeedDegs="840">
              <ModifierList type="deny-list">
              <command>strafe</command>
              </ModifierList>
              </ContinuousMovementCommands>
              <ChatCommands />
              <AgentQuitFromTouchingBlockType>
                <Block type="diamond_block" />
              </AgentQuitFromTouchingBlockType>
              </AgentHandlers>
              </AgentSection>
              
              <AgentSection mode="Survival">
              <Name>Gertrude</Name>
              <AgentStart>
              <Placement x="-4.5" y="9.0" z="0.5"/>
              </AgentStart>
              <AgentHandlers>
              <ObservationFromChat />
              <ContinuousMovementCommands turnSpeedDegs="840">
              <ModifierList type="deny-list"> <!-- Example deny-list: prevent agent from strafing -->
              <command>strafe</command>
              </ModifierList>
              </ContinuousMovementCommands>
              <ChatCommands />
              <AgentQuitFromTouchingBlockType>
                <Block type="diamond_block" />
              </AgentQuitFromTouchingBlockType>
              </AgentHandlers>
              </AgentSection>


            </Mission>'''

# Create default Malmo objects:

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
agent_host = MalmoPython.AgentHost()
agent_host.addOptionalIntArgument( "role,r", "For multi-agent missions, the role of this agent instance", 0)
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print 'ERROR:',e
    print agent_host.getUsage()
    exit(1)
if agent_host.receivedArgument("help"):
    print agent_host.getUsage()
    exit(0)

role = agent_host.getIntArgument("role")
print "Will run as role",role

agent_host.setObservationsPolicy(MalmoPython.ObservationsPolicy.LATEST_OBSERVATION_ONLY)

# Create a client pool here - this assumes two local mods with default ports,
# but you could have two mods on different machines, and specify their IP address here.
client_pool = MalmoPython.ClientPool()
client_pool.add( MalmoPython.ClientInfo( "127.0.0.1", 10000 ) )
client_pool.add( MalmoPython.ClientInfo( "127.0.0.1", 10001 ) )

chat_frequency = 30 # if we send chat messages too frequently the agent will be disconnected for spamming
num_steps_since_last_chat = 0

my_mission = MalmoPython.MissionSpec(missionXML, True) #This loads the xml file, you could change True to variable to make sure the instance is valid before loading
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
if role==0:
    pflag=0
    while world_state.is_mission_running:
        world_state = agent_host.getWorldState()
        if world_state.number_of_observations_since_last_state > 0:
            msg = world_state.observations[-1].text
            ob = json.loads(msg)
            if "Nearby" in ob:
                entities = [EntityInfo(**k) for k in ob["Nearby"]]
                for ent in entities:
                    print (ent.name)
                    if ent.name=="Typhoonizm":
                        foundPlayer()
                        flag=1
            if "Player" in ob:
                far_entities = [EntityInfo(**k) for k in ob["Player"]]
        
            if flag==0:
                lostPlayer()
                flag=2
else:
    while world_state.is_mission_running:
        sys.stdout.write(".")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print "Error:",error.text


print
print "Mission ended"
# Mission has ended.




