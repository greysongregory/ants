'''
Created on Oct 1, 2011

@author: djweiss
'''
from antpathsearch import aStarSearch

EXPLORED_MAX = 100
EXPLORED_STEP = 5
FOG = 8

class FeatureExtractor:
    ''' Extracts features from ant world state for given actions.
    
    This is the template class for all feature extractors. 
    A feature extractor must implement the init_from_dict() and extract() methods.  
    '''
    
    def __init__(self, input_dict):
        self.search = aStarSearch()
        ''' Create a new FeatureExtractor from a dict object.'''
        
        new_type = input_dict['_type']
        if new_type == BasicFeatures.type_name: 
            self.__class__ = BasicFeatures
        elif new_type == QualifyingFeatures.type_name:
            self.__class__ = QualifyingFeatures
        elif new_type == CompositingFeatures.type_name:
            self.__class__ = CompositingFeatures 
        elif new_type == AdvancedFeatures.type_name:
            self.__class__ = AdvancedFeatures
        else:
            raise Exception("Invalid feature class %s" + new_type)

        self.feature_names = []
        self.feature_id = {}
        
        # Call class-specific initialization.    
        self.init_from_dict(input_dict)
        
        fid = 0
        for name in self.feature_names:
            self.feature_id[name] = fid
            fid += 1

    def __str__(self):
        return str(self.__class__)
        
    def to_dict(self):
        """Convert FeatureExtractor to a human readable dict."""
        
        return {'_type': self.__class__.type_name}

    def num_features(self):
        """Size of feature vector output by this extractor."""
        
        return len(self.feature_names)
    
    def feature_name(self, fid):
        """Get the name of the fid'th feature as a string.""" 
        
        return self.feature_names[fid]
    
    def feature_id(self, name):
        """Reverse lookup the feature id of the specified feature name."""
        
        return self.feature_id[name]
       
    def init_from_dict(self, input_dict):
        """Perform any class-specific initialization, grabbing parameters from input_dict.""" 
        raise NotImplementedError
        
    def extract(self, world, state, loc, action):
        """Extracts a feature vector from a world, state, location, and action. 
        
        Feature vectors are lists of booleans, where length = num_features() regardless of 
        the # of active features.
        """
        
        raise NotImplementedError


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
        self.feature_names.append("Moving on A* path Towards hill")
       
        self.feature_names.append("Friendly adjacent")

        for x in range(1, FOG+1):
            self.feature_names.append("Closest friendly hill "+str(x)+" away")
        self.feature_names.append("Closest friendly hill > "+str(x)+" away")

        for x in range(1, FOG+1):
            self.feature_names.append("Closest enemy hill "+str(x)+" away")
        self.feature_names.append("Closest enemy hill > "+str(x)+" away")

        for x in range(1, FOG+1):
            self.feature_names.append("Closest food "+str(x)+" away")
        self.feature_names.append("Closest food > "+str(x)+" away")
        
        for x in range(1, FOG+1):
            self.feature_names.append("Closest enemy "+str(x)+" away")
        self.feature_names.append("Closest enemy > "+str(x)+" away")
        
        for x in range(EXPLORED_STEP, EXPLORED_MAX, EXPLORED_STEP):
            self.feature_names.append("Area Explored "+str(x)+" times recently");
        
        
        
        
        
        ##---------Grey's qualifiers here------##
        self.feature_names.append("Is One From Attack")
        self.feature_names.append("Is Two From Attack")
        self.feature_names.append("Is Three From Attack")
        self.feature_names.append("Is Four From Attack")
        self.feature_names.append("Is Five From Attack") 
        self.feature_names.append("Is At Least Twice Enemy Army")
        self.feature_names.append("Is At Least One and a Half Enemy Army")
        self.feature_names.append("Is At Least Equal Enemy Army")
        self.feature_names.append("Is Closest Ant to Closest Food")
        self.feature_names.append("Is Closer to Food than Enemy")

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
        
        path = self.search.get_path(world, loc, dest)
        if path is None:
            return False
        if 1 not in path:
            return False
        return next_loc == path[1];
    
    def extractVinFeatures(self, world, state, loc, action):
        """Extract the three simple features."""
        
        food_loc = self.find_closest(world, loc, state.lookup_nearby_food(loc))
        enemy_loc = self.find_closest(world, loc, state.lookup_nearby_enemy(loc))
        friend_loc = self.find_closest(world, loc, state.lookup_nearby_friendly(loc))
        my_hill_loc = self.find_closest(world, loc, world.enemy_hills())
        enemy_hill_loc = self.find_closest(world, loc, world.my_hills())


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
            

        # Moving towards enemy hill
        if enemy_hill_loc is None:
            f.append(False)
        else:
            f.append(self.movingOnAStarPath(world, loc, next_loc, enemy_hill_loc));

        
        # adjacent friendly
        if friend_loc is None:
            f.append(False)
        else:
            f.append(world.manhattan_distance(next_loc,friend_loc)==1)
            
                    
        # closest hill_loc {1,2,3,4} away
        if my_hill_loc is None:
            f += [False]*(int(FOG+1))
        else:
            d_hill = world.manhattan_distance(next_loc, my_hill_loc)
            for k in range(1,FOG+1):
                f.append(d_hill == k)
            f.append(d_hill > FOG)
        
        
        # closest hill_loc {1,2,3,4} away
        if enemy_hill_loc is None:
            f += [False]*(int(FOG+1))
        else:
            d_hill = world.manhattan_distance(next_loc,enemy_hill_loc)
            for k in range(1,FOG+1):
                f.append(d_hill == k)
            f.append(d_hill > FOG)
            
            
            
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
            f += [False]*EXPLORED_MAX/EXPLORED_STEP
        else:
            for k in range(EXPLORED_STEP, EXPLORED_MAX, EXPLORED_STEP):
                f.append(explored <= k)
        
        return f
        
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
        
        return f
    
    
    
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
        dist = world.euclidean_distance2(loc, enemy_loc)
        spaces = -1
        for i in range(1, 7):
            if dist < spaces_to_distance:
                spaces = i
        
        return spaces is 5
    
    def is_four_from_attack(self, world, state, loc, action, spaces_to_distance):
        enemy_loc = self.find_closest(world, loc, state.lookup_nearby_enemy(loc))
        if enemy_loc is None:
            return False
        dist = world.euclidean_distance2(loc, enemy_loc)
        spaces = -1
        for i in range(1, 7):
            if dist < spaces_to_distance:
                spaces = i
        
        return spaces is 4
    
    def is_three_from_attack(self, world, state, loc, action, spaces_to_distance):
        enemy_loc = self.find_closest(world, loc, state.lookup_nearby_enemy(loc))
        if enemy_loc is None:
            return False
        dist = world.euclidean_distance2(loc, enemy_loc)
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
        dist = world.euclidean_distance2(loc, enemy_loc)
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
        dist = world.euclidean_distance2(loc, enemy_loc)
        spaces = -1
        for i in range(1, 7):
            if dist < spaces_to_distance:
                spaces = i
        
        return spaces is 1
    
    def extract(self, world, state, loc, action):
        features = list()
        features.extend(self.extractVinFeatures(world, state, loc, action))
        features.extend(self.extractBetterThanVinFeatures(world, state, loc, action))
        return features



class BasicFeatures(FeatureExtractor):
    """Very basic features.
    
    Computes three features: whether or not a given action takes an ant nearer to its closest
    enemy, food, or friendly ant.
    """
    
    type_name = 'Basic'
       
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
        FeatureExtractor.__init__(self, {'_type': BasicFeatures.type_name})    
                
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
    


class QualifyingFeatures(FeatureExtractor):
    """Additional qualifier-type features.
    
    This is part of the assignment for HW3. Your features in this class don't have to depend on
    the action, but instead can be functions of state or location, e.g., "1 ant left".
    
    """
    
    type_name = 'Qualifying'    
    
    def __init__(self):
        pass
        
    def init_from_dict(self, input_dict):
        self.feature_names.append("Moving Towards Closest Enemy")
        self.feature_names.append("Moving Towards Closest Food")
        self.feature_names.append("Moving Towards Friendly")
    
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
        
        return f
    
    
class CompositingFeatures(FeatureExtractor):
    """Generates new features from new existing FeatureExtractors.
    
    This is part of the assignment for HW3. CompositingFeatures takes two FeatureExtractors,
    base_f and qual_f. If len(base_f) = n and len(qual_f) = m, then this extractor generates 
    n(m+1) features consisting of the original base_f features plus a copy of base_f features 
    that is multiplied by each of the qual_f features.
    
    It is important to compute the unique names of each feature to help with debugging.

    """
    
    type_name = 'Compositing'        

    def __init__(self, base_f, qual_f):
        FeatureExtractor.__init__(self, {'_type': CompositingFeatures.type_name, 
                                         'base_f' : base_f.to_dict(), 'qual_f': qual_f.to_dict()})
    
             
    def init_from_dict(self, input_dict):
        self.base_f = FeatureExtractor(input_dict['base_f']) 
        self.qual_f = FeatureExtractor(input_dict['qual_f']) 

        # Compute names based on the features we've loaded    
        self.compute_feature_names()

    def to_dict(self):
        val =  FeatureExtractor.to_dict(self)
        val['base_f'] = self.base_f.to_dict()
        val['qual_f'] = self.qual_f.to_dict()
        return val
        
    def compute_feature_names(self):
        """ Compute the list of feature names from the composition of base_f and qual_f. The
        features should be organized as follows. If base_f has n features and qual_f has m features,
        then the features are indexed as follows:
        
        f[0] through f[n-1]: base_f[0] through base_f[n-1]
        f[n] through f[2n-1]: base_f[0]*qual_f[0] through base_f[n]*qual_f[0] 
        ...
        f[mn] through f[(m+1)n-1]: base_f[n-1]*qual_f[m-1] through base_f[n-1]*qual_f[m-1] 
                
        """
        self.feature_names.extend(self.base_f.feature_names)
#        for i in range(len(self.base_f.feature_names)):
#            self.feature_names.append('NOT ' + self.base_f.feature_names[i])
        for i in range(len(self.base_f.feature_names)):
            for j in range(len(self.qual_f.feature_names)):
                self.feature_names.append(self.base_f.feature_names[i] + '+' + self.qual_f.feature_names[j])
        
    
    def extract(self, world, state, loc, action):
        """Extracts the combination of features according to the ordering defined by compute_feature_names()."""
        feats1 = self.base_f.extract(world, state, loc, action)
        feats2 = self.qual_f.extract(world, state, loc, action)
        f = [ff*1.0 for ff in feats1]
        for f1 in feats1:
            for f2 in feats2:
                f.append(1.0*f1*f2)
                
        return f
