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

    <DrawBlock x="14" y="9" z="4" type="mob_spawner" variant="Zombie" />
    <DrawBlock x="-6" y="9" z="4" type="mob_spawner" variant="Zombie" />
    <DrawBlock x="4" y="9" z="14" type="mob_spawner" variant="Zombie" />
    <!--<DrawBlock x="4" y="9" z="-6" type="mob_spawner" variant="Zombie" />-->
    
    </DrawingDecorator>
    <ServerQuitWhenAnyAgentFinishes/>
    </ServerHandlers>
    </ServerSection>
    
    <AgentSection mode="Survival">
    <Name>Burton</Name>
    <AgentStart>
    <Placement x="0.5" y="9.0" z="0.5"/>
    <Inventory>
        <InventoryItem slot="36" type="diamond_boots"/>
        <InventoryItem slot="37" type="diamond_leggings"/>
        <InventoryItem slot="38" type="diamond_chestplate"/>
        <InventoryItem slot="39" type="diamond_helmet"/>
        <InventoryItem slot="0" type="diamond_sword"/>
    </Inventory>
    </AgentStart>
    <AgentHandlers>
    <ObservationFromChat />
    <ObservationFromNearbyEntities>
    <Range name="Nearby" xrange="2" yrange="2" zrange="2" update_frequency="1"/>
    <Range name="Player" xrange="50" yrange="2" zrange="50" update_frequency="1"/>
    <Range name="Mob" xrange="20" yrange="2" zrange="20" update_frequency="1"/>
    </ObservationFromNearbyEntities>
    <ObservationFromFullStats/>
    <ObservationFromGrid>
    <Grid name="floorGrid">
    <min x="-10" y="-1" z="-10"/>
    <max x="10" y="1" z="10"/>
    </Grid>
    </ObservationFromGrid>
    <ContinuousMovementCommands turnSpeedDegs="180">
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
