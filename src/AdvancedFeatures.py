'''
Created on Dec 6, 2011

@author: Vin
'''

'''
Created on Dec 6, 2011

@author: Vin
'''

from features import FeatureExtractor

class AdvancedFeatures(FeatureExtractor):
    '''
    classdocs
    '''

    type_name = 'Advanced'
       
    def init_from_dict(self, input_dict):
        
        self.feature_names.append("Moving Towards Closest Enemy")
        self.feature_names.append("Moving Towards Closest Food")
        self.feature_names.append("Moving Towards Friendly")
       
        self.feature_names.append("Friendly adjacent")

        self.feature_names.append("Closest food 1 away")
        self.feature_names.append("Closest food 2 away")
        self.feature_names.append("Closest food 3 away")
        self.feature_names.append("Closest food 4 away")
        self.feature_names.append("Closest food > 4 away")
        
        self.feature_names.append("Closest enemy 1 away")
        self.feature_names.append("Closest enemy 2 away")
        self.feature_names.append("Closest enemy 3 away")
        self.feature_names.append("Closest enemy 4 away")
        self.feature_names.append("Closest enemy >4 away")

    def __init__(self):
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
            f.append(self.moving_towards(world, loc, next_loc, enemy_loc));
        
        # Moving towards food
        if food_loc is None:
            f.append(False)
        else:
            f.append(self.moving_towards(world, loc, next_loc, food_loc));
        
        # Moving towards friendly
        if friend_loc is None:
            f.append(False)
        else:
            f.append(self.moving_towards(world, loc, next_loc, friend_loc));
            
        # adjacent friendly
        if friend_loc is None:
            f.append(False)
        else:
            f.append(world.manhattan_distance(next_loc,friend_loc)==1)
            
        # closest food {1,2,3,4} away
        if food_loc is None:
            f += [False]*5
        else:
            d_food = world.manhattan_distance(next_loc,food_loc)
            for k in range(1,5):
                f.append(d_food == k)
            f.append(d_food > 4)
                
        # closest enemy {1,2,3,4} away
        if enemy_loc is None:
            f += [False]*5
        else:
            d_enemy = world.manhattan_distance(next_loc,enemy_loc)
            for k in range(1,5):
                f.append(d_enemy == k)
            f.append(d_enemy > 4)
        
        return f