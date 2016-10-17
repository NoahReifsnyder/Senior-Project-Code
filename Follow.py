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

# A* Search Solution for Tutorial sample #7: The Maze Decorator

# Note: I wrote this code quickly, and did a simple pass to make sure it's somewhat readable.
# Probably not as efficient or optimized as it could be (almost sure of it).
# I bet there are multiple places it could be improved, feel free to do whatever you'd like with it.

import MalmoPython
import os
import sys
import time
import json
import copy
from MIDCA import goals

class Node():
    '''
    a node that will be used in A* search
    '''
    agent_loc = None # x, y coordinate
    state = None # all_tiles in a grid
    parent_node = []
    actions_taken = [] # actions taken to reach this node
    depth = 0
    
    def __init__(self, agent_loc, state, parent_node, actions_taken):
        self.agent_loc = agent_loc
        self.state = state
        self.parent_node = parent_node
        if parent_node:
            self.depth = parent_node.depth+1
        else:
            self.depth = 0
        self.actions_taken = actions_taken

    def __str__(self):
        s = "aloc="+str(self.agent_loc)+"state_x_len="+str(len(self.state))+"state_y_len"+str(len(self.state[0]))
        return s


def get_child_nodes(node, curr_nodes, already_visited_nodes, grid):
    if not node: # sanity check
        return []
    
    x = node.agent_loc[0]
    y = node.agent_loc[1]
    
    valid_child_nodes = []
    
    # add each action
    if x != len(grid[y]) and grid[x + 1, y] == 1:
        # make a copy just to make sure we are not modifying some
        # node some other place
        e_actions = copy.deepcopy(node.actions_taken) 
        e_actions.append("movewest 1")
        east_node = Node((x + 1, y), grid,node,e_actions)
        valid_child_nodes.append(east_node) #east node
    if x != 0 and grid[x - 1, y] == 1:
        w_actions = copy.deepcopy(node.actions_taken)
        w_actions.append("moveeast 1")
        west_node = Node((x - 1,y),grid,node,w_actions)
        valid_child_nodes.append(west_node) # west node
    if y != len(grid) and grid[x, y + 1] == 1:
        s_actions = copy.deepcopy(node.actions_taken)
        s_actions.append("movesouth 1")
        south_node = Node((x, y + 1),grid,node,s_actions)
        valid_child_nodes.append(south_node) #east node
    if y != 0 and grid[x, y - 1] == 1:
        n_actions = copy.deepcopy(node.actions_taken)
        n_actions.append("movenorth 1")
        north_node = Node((x, y - 1),grid,node,n_actions)
        valid_child_nodes.append(north_node) # west node

    # filter out anything that is already in curr_nodes (may not be necessary)
    curr_node_locs = map(lambda n: n.agent_loc,curr_nodes)
    valid_child_nodes = filter(lambda n: n.agent_loc not in curr_node_locs, valid_child_nodes)
    
    # filter out anything that we have already visited (necessary, prevents cycles)
    visited_node_locs = map(lambda n: n.agent_loc,already_visited_nodes)
    valid_child_nodes = filter(lambda n: n.agent_loc not in visited_node_locs, valid_child_nodes)
    return valid_child_nodes


def A_star_search(playerx, playery, grid):
    # find the location of the emerald block, record this as agent's position and start
    # also find location of redstone block, save as goal loc
    agent_loc_x = 0
    agent_loc_y = 0

    goal_x = playerx
    goal_y = playery

    print "agent_loc = " +str(agent_loc_x) + ","+str(agent_loc_y)
    print "goal_loc = "+str(goal_x) + ","+str(goal_y)
    
    # safety check, make sure start and goal are not the same
    if str(agent_loc_x) + ","+str(agent_loc_y) == str(goal_x) + ","+str(goal_y):    
        return []
    
    # root node
    root_node = Node((agent_loc_x, agent_loc_y),grid,None,[])
    
    def goal_reached(node):
        reached = False
        try:
            reached = grid[node.agent_loc[1]][node.agent_loc[0]] == 3
        except:
            print "somehow it broked with y="+str(node.agent_loc[1])+", x="+str(node.agent_loc[1])  
        return reached
    
    def manhattan_dist_to_goal(node):
        #print "g(n)="+str((abs(goal_x - node.agent_loc[0])+abs(goal_y-node.agent_loc[1])))+",h(n)="+str(node.depth)
        return (abs(goal_x - node.agent_loc[0])+abs(goal_y-node.agent_loc[1])) + node.depth
    
    def depth_and_manhatten(node):
        return manhattan_dist_to_goal(node) 

    # initialize the queue with the first node
    curr_nodes = [root_node]
    already_visited_nodes = []
    while len(curr_nodes) > 0 and not goal_reached(curr_nodes[0]):
        # get first node from our queue
        curr_node = curr_nodes[0]
        curr_nodes = curr_nodes[1:] # take the first node off
        
        # save this node so we don't visit again
        already_visited_nodes.append(curr_node)
        
        # get child nodes
        child_nodes = get_child_nodes(copy.deepcopy(curr_node),curr_nodes, already_visited_nodes)
                
        # add child nodes to queue
        curr_nodes += child_nodes
        
        # sort queue based on manhatten + depth
        curr_nodes = sorted(curr_nodes,key=depth_and_manhatten)
        
        #print "already_visited_nodes = "+str(map(lambda n: n.agent_loc, already_visited_nodes))
        print "Q = " +str(map(lambda n: "f(n)="+str(depth_and_manhatten(n))+",xy="+str(n.agent_loc), curr_nodes))
        #print "queue (depths) = "+str(map(lambda n: n.depth, curr_nodes))
        #print "queue size = " +str(len(curr_nodes))
        #print "queue distances to goal: "+str(map(depth_and_manhatten,curr_nodes))
        # sort nodes based on depth (bfs for now)
        
        #time.sleep(0.1)
       
    # make sure goal was reached
    if not goal_reached(curr_nodes[0]):
        print "ERROR: search terminated without finding a path"
    else:
        print "computed path:"
        for action in curr_nodes[0].actions_taken:
            print "  " + str(action)
        return curr_nodes[0].actions_taken
