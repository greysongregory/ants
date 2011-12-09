'''
Created on Aug 23, 2011

@author: bensapp
'''
from antsgame import AIM
import heapq
import math

class AntPathSearch():
    ''' This is a base class for all specific search classes. '''
    
    def __init__(self):
        pass
        
    def get_path(self,start,goal):
        ''' 
        Input: start and goal are both 2-tuples containing (x,y) coordinates
        Output: Returns a list of 2-tuples which are a sequence of locations to get from START to GOAL
            - path[0] should equal START
            - path[-1] should equal GOAL
            - path[i+1] should be reachable from path[i] via exactly one step in some cardinal direction, for all i
        '''
        raise NotImplementedError
        
    def get_successors(self, world, loc):
        ''' 
        Returns a list of valid next reachable locations from the input LOC.
        All derived classes should use this function, otherwise testing your implementation might fail.        
        '''
        
        alldirs = AIM.keys()
        s = []
        for d in alldirs:
            l = world.next_position(loc, d)
            if world.passable(l) and world.ant_lookup[l] == -1:
                s.append(l)
        return s
         

class BreadthFirstSearch(AntPathSearch):
    
    def get_path(self,start,goal):
        queue = [start]
        visited = {}
        discovered = {start : True}
        parents = {start : None}
        while len(queue) > 0:
            node = queue.pop()
            if node == goal:
                path = [goal]
                parent = parents[goal]
                while parent is not None:
                    path.insert(0, parent)
                    parent = parents[parent]
                return path
            if node not in visited:
                visited[node] = True
                for successor in self.get_successors(node):
                    if successor not in discovered and successor not in visited:
                        discovered[successor] = True
                        parents[successor] = node
                        queue.insert(0, successor)
        return None
        
        
class DepthFirstSearch(AntPathSearch):
    
    def get_path(self,start,goal):
        stack = [start]
        visited = {}
        discovered = {start : True}
        while len(stack) > 0:
            node = stack.pop()
            if node == goal:
                path = [goal]
                while len(stack) > 0:
                    n = stack.pop()
                    if n in visited:
                        path.insert(0, n)
                return path
            if node not in visited:
                visited[node] = True
                successors = self.get_successors(node)
                if len(successors) > 0:
                    stack.append(node)
                    for successor in successors:
                        if successor not in discovered and successor not in visited:
                            discovered[successor] = True
                            stack.append(successor)
        return None
    
    
class aStarSearch(AntPathSearch):
    
    def __init__(self):
        self.cached_paths = {}
        self.cached = 0
        self.uncached = 0
    
    def cache_rate(self):
        if self.cached == 0 and self.uncached == 0:
            return 0
        return float(self.cached)/(self.cached+self.uncached)
    
    #use manhattan distance
    def heuristic_cost(self, state,goal):
        return math.fabs(goal[0]-goal[1]) + math.fabs(state[0]-state[1])
    
    def get_path(self, world, start,goal):
        if goal in self.cached_paths and start in self.cached_paths[goal]:
            self.cached += 1
            return self.cached_paths[goal][start]
        
        else:
            self.uncached += 1
            visited = {}
            g = {start : 0}
            h = {}
            f = {}
            discovered = {}
            parents = {start: None}
            queue = []
            heapq.heappush(queue, (0, start))
            while len(queue) > 0:    
                (priority, node) = heapq.heappop(queue)
                if node == goal:
                    path = [goal]
                    parent = parents[goal]
                    while parent is not None:
                        path.insert(0, parent)
                        if parent not in self.cached_paths:
                            self.cached_paths[goal] = {}
                        self.cached_paths[goal][parent] = path
                        parent = parents[parent]
                    return path
                if node not in visited:
                    visited[node] = True
                    for succ in self.get_successors(world, node):
                        if succ not in discovered and succ not in visited:
                            discovered[succ] = True
                            parents[succ] = node
                            g[succ] = g[node]+1
                            h[succ] = self.heuristic_cost(succ, goal)
                            f[succ] = g[succ]+h[succ]
                            heapq.heappush(queue, (f[succ], succ))
            return None
        
        
        
        
        