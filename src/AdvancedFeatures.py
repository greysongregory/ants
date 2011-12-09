'''
Created on Dec 6, 2011

@author: Vin
'''

from features import FeatureExtractor
from antpathsearch import aStarSearch
#Constants
#vin
EXPLORED_TURNS_MAX = 100
EXPLORED_TURNS_STEP = 5

FOG = 8
class AdvancedFeatures(FeatureExtractor):
    '''
    classdocs
    '''

    type_name = 'Advanced'
       
    def init_from_dict(self, input_dict):
        
        ##------Vin's qualifiers go here----##
        
        #Change to a*
        self.feature_names.append("Moving on A* path Closest Enemy")
        self.feature_names.append("Moving on A* path Towards Closest Food")
        self.feature_names.append("Moving on A* path Towards Friendly")
       
        self.feature_names.append("Friendly adjacent")

        for x in range(1, FOG+1):
            self.feature_names.append("Closest food "+str(x)+" away")
        self.feature_names.append("Closest food > "+str(x)+" away")
        
        for x in range(1, FOG+1):
            self.feature_names.append("Closest enemy "+str(x)+" away")
        self.feature_names.append("Closest enemy > "+str(x)+" away")
        
        for x in range(EXPLORED_TURNS_STEP, EXPLORED_TURNS_MAX, EXPLORED_TURNS_STEP):
            self.feature_names.append("Explored "+str(x)+" turns ago");
        self.feature_names.append("Explored more than"+str(EXPLORED_TURNS_MAX)+" turns ago");
        
        
        
        
        
        ##---------Grey's qualifiers here------##
        

    def __init__(self):
        
        FeatureExtractor.__init__(self, {'_type': AdvancedFeatures.type_name}) 
        self.search = aStarSearch()
           
                
    def moving_towards(self, world, loc1, loc2, target):
        """Returns true if loc2 is closer to target than loc1 in manhattan distance."""
        
        return world.manhattan_distance(loc1, target) - world.manhattan_distance(loc2, target) > 0

    def find_closest(self, world, loc, points):
        """Returns the closest point to loc from the list points, or None if points is empty."""
        if len(points) == 1:
            return points[0]
        
        locs = world.sort_by_distance(loc, points)
            
        if len(locs) > 0:
            return locs[0][1]
        else:
            return None
        
    def movingOnAStarPath(self, world, loc, next_loc, dest):
        #for a* path: 0th index is start location, 1st is next loc
        
        return self.moving_towards(world, loc, next_loc, dest)
        
        path = self.search.get_path(world, loc, dest)
        if path is None:
            return False
        return next_loc == path[1];
        
    
    def extractVinFeatures(self, world, state, loc, action):
        """Extract the three simple features."""
        
        food_loc = self.find_closest(world, loc, state.lookup_nearby_food(loc))
        enemy_loc = self.find_closest(world, loc, state.lookup_nearby_enemy(loc))
        friend_loc = self.find_closest(world, loc, state.lookup_nearby_friendly(loc))


        next_loc = world.next_position(loc, action)
        world.L.debug("loc: %s, food_loc: %s, enemy_loc: %s, friendly_loc: %s" % (str(loc), str(food_loc), str(enemy_loc), str(friend_loc)))
        # Feature vector        
        f = list()
        
        # Moving towards enemy
        if enemy_loc is None:
            f.append(False)
        else:
            f.append(self.movingOnAStarPath(world, loc, next_loc, enemy_loc));
        
        # Moving towards food
        if food_loc is None:
            f.append(False)
        else:
            f.append(self.movingOnAStarPath(world, loc, next_loc, food_loc));
        
        # Moving towards friendly
        if friend_loc is None:
            f.append(False)
        else:
            f.append(self.movingOnAStarPath(world, loc, next_loc, friend_loc));
            
        print self.search.cache_rate()
        
        # adjacent friendly
        if friend_loc is None:
            f.append(False)
        else:
            f.append(world.manhattan_distance(next_loc,friend_loc)==1)
            
        # closest food {1,2,3,4} away
        if food_loc is None:
            f += [False]*(int(FOG+1))
        else:
            d_food = world.manhattan_distance(next_loc,food_loc)
            for k in range(1,FOG+1):
                f.append(d_food == k)
            f.append(d_food > FOG)
                
        # closest enemy {1,2,3,4} away
        if enemy_loc is None:
            f += [False]*(int(FOG+1))
        else:
            d_enemy = world.manhattan_distance(next_loc,enemy_loc)
            for k in range(1,FOG+1):
                f.append(d_enemy == k)
            f.append(d_enemy > FOG)
        
        
        explored = state.get_visited(loc)
        if explored is None:
            f += [False]*EXPLORED_TURNS_MAX/EXPLORED_TURNS_STEP+1
        else:
            for k in range(EXPLORED_TURNS_STEP, EXPLORED_TURNS_MAX, EXPLORED_TURNS_STEP):
                f.append(explored <= k)
            f.append(explored > EXPLORED_TURNS_MAX)
        
        return f
        
        
    def extractGreyFeatures(self, world, state, loc, action):
        pass
    
    def extract(self, world, state, loc, action):
        return self.extractVinFeatures(world, state, loc, action)
