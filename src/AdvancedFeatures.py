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
        

    def __init__(self, world):
        FeatureExtractor.__init__(self, {'_type': AdvancedFeatures.type_name}) 
           
                
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
        
<<<<<<< HEAD
    def extractVinFeatures(self, world, state, loc, action):
        pass
    
    def extractBetterThanVinFeatures(self, world, state, loc, action):
        spaces_to_distance = state.create_moves_required_to_get_attacked()
        
        f = list()
        
        f.append(self.is_one_from_attack(world, state, loc, action, spaces_to_distance))
        f.append(self.is_two_from_attack(world, state, loc, action, spaces_to_distance))
        f.append(self.is_three_from_attack(world, state, loc, action, spaces_to_distance))
        f.append(self.is_four_from_attack(world, state, loc, action, spaces_to_distance))
        f.append(self.is_five_from_attack(world, state, loc, action, spaces_to_distance))
        f.append(self.is_at_least_twice_enemy_army(world, state, loc, action))
        f.append(self.is_at_least_oneandahalf_enemy_army(world, state, loc, action))
        f.append(self.is_at_least_equal_enemy_army(world, state, loc, action))
        f.append(self.is_closest_ant_to_closest_food(world, state, loc, action))
        f.append(self.is_closer_to_food_than_enemy(world, state, loc, action))
        pass
    
    
    
    def is_closer_to_food_than_enemy(self, world, state, loc, action):
        food_loc = self.find_closest(world, loc, state.lookup_nearby_food(loc))
        if food_loc is None:
            return False
        closest_enemy_to_food = self.find_closest(world, food_loc, state.lookup_nearby_enemy(food_loc))
        if closest_enemy_to_food is None:
            return True
        enemy_dist = world.manhattan_distance(food_loc, closest_enemy_to_food)
        ant_dist = world.manhattan_distance(food_loc, loc)
        
        return ant_dist < enemy_dist 
    
    def is_closest_ant_to_closest_food(self, world, state, loc, action):
        food_loc = self.find_closest(world, loc, state.lookup_nearby_food(loc))
        if food_loc is None:
            return False
        closest_ant_to_food = self.find_closest(world, food_loc, state.lookup_nearby_friendly(food_loc))
        
        return closest_ant_to_food is loc
    
    def is_at_least_equal_enemy_army(self, world, state, loc, action):
        enemies = state.lookup_nearby_enemy(loc)
        friendlies = state.lookup_nearby_friendly(loc)
        
        return (len(friendlies) >= len(enemies))
    
    def is_at_least_oneandahalf_enemy_army(self, world, state, loc, action):
        enemies = state.lookup_nearby_enemy(loc)
        friendlies = state.lookup_nearby_friendly(loc)
        
        return (len(friendlies) >= 1.5*len(enemies))
    
    def is_at_least_twice_enemy_army(self, world, state, loc, action):
        enemies = state.lookup_nearby_enemy(loc)
        friendlies = state.lookup_nearby_friendly(loc)
        
        return (len(friendlies) >= 2*len(enemies))
    
    def is_five_from_attack(self, world, state, loc, action, spaces_to_distance):
        enemy_loc = self.find_closest(world, loc, state.lookup_nearby_enemy(loc))
        if enemy_loc is None:
            return False
        dist = world.euclidian_distance(loc, enemy_loc)
        spaces = -1
        for i in range(1, 7):
            if dist < spaces_to_distance:
                spaces = i
        
        return spaces is 5
    
    def is_four_from_attack(self, world, state, loc, action, spaces_to_distance):
        enemy_loc = self.find_closest(world, loc, state.lookup_nearby_enemy(loc))
        if enemy_loc is None:
            return False
        dist = world.euclidian_distance(loc, enemy_loc)
        spaces = -1
        for i in range(1, 7):
            if dist < spaces_to_distance:
                spaces = i
        
        return spaces is 4
    
    def is_three_from_attack(self, world, state, loc, action, spaces_to_distance):
        enemy_loc = self.find_closest(world, loc, state.lookup_nearby_enemy(loc))
        if enemy_loc is None:
            return False
        dist = world.euclidian_distance(loc, enemy_loc)
        spaces = -1
        for i in range(1, 7):
            if dist < spaces_to_distance:
                spaces = i
        
        return spaces is 3
        
    def is_two_from_attack(self, world, state, loc, action, spaces_to_distance):
        #tests to see if the ant is currently on the "edge" of potential attack radius of an enemy ON ITS NEXT TURN
        #this guarantee that this ant will not die on next turn
        enemy_loc = self.find_closest(world, loc, state.lookup_nearby_enemy(loc))
        if enemy_loc is None:
            return False
        dist = world.euclidian_distance(loc, enemy_loc)
        spaces = -1
        for i in range(1, 7):
            if dist < spaces_to_distance:
                spaces = i
        
        return spaces is 2
                    
    def is_one_from_attack(self, world, state, loc, action, spaces_to_distance):
        #tests to see if the ant is one space from the attack radius of an enemy ant 
        #not engaging the enemy, but if the enemy moves toward us, let the battles begin
        enemy_loc = self.find_closest(world, loc, state.lookup_nearby_enemy(loc))
        if enemy_loc is None:
            return False
        dist = world.euclidian_distance(loc, enemy_loc)
        spaces = -1
        for i in range(1, 7):
            if dist < spaces_to_distance:
                spaces = i
        
        return spaces is 1
            
    def extract(self, world, state, loc, action):
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
            f.append(self.moving_towards(world, loc, next_loc, enemy_loc))
        
        # Moving towards food
        if food_loc is None:
            f.append(False)
        else:
            f.append(self.moving_towards(world, loc, next_loc, food_loc))
        
        # Moving towards friendly
        if friend_loc is None:
            f.append(False)
        else:
            f.append(self.movingOnAStarPath(world, loc, next_loc, friend_loc));
            
        # adjacent friendly
        if friend_loc is None:
            f.append(False)
        else:
            f.append(world.manhattan_distance(next_loc,friend_loc)==1)
            
        # closest food {1,2,3,4} away
        if food_loc is None:
            f += [False]*FOG+1
        else:
            d_food = world.manhattan_distance(next_loc,food_loc)
            for k in range(1,FOG+1):
                f.append(d_food == k)
            f.append(d_food > FOG)
                
        # closest enemy {1,2,3,4} away
        if enemy_loc is None:
            f += [False]*FOG+1
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
