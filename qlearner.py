'''
Created on Oct 19, 2011

@author: bensapp
'''
from src.worldstate import AIM, AntStatus, RewardEvents
from src.mapgen import SymmetricMap
from src.features import CompositingFeatures, AdvancedFeatures
from src.state import GlobalState
from antpathsearch import aStarSearch
from valuebot import ValueBot
import random
from src.localengine import LocalEngine
from greedybot import GreedyBot
import sys
import math
import time


LIVING_REWARD = -1
FOOD_REWARD = 19
DEATH_REWARD = -4
KILL_REWARD = 14
RAZED_REWARD = 50
EXPLORE_THRESHOLD = 10
ALPHA_DIVIDER = 5
DISCOUNT = .6
PLAY_TYPE = 'play'


class QLearnBot(ValueBot):
    
    def __init__(self,world, load_file="save_bots/qbot.json"):
        self.world = world
        ValueBot.__init__(self,world, load_file)
        self.nturns = 0
        self.pathfinder = None
    
    def get_reward(self,reward_state):
        """ 
        Hand-tuned rewards for a state.  The RewardState reward_state tracks the
        following events for which you can tailor rewards:
            reward_state.food_eaten: Fraction of a food item this ant ate (between 0 and 1)
            reward_state.was_killed: boolean flag whether the ant died this turn
            reward_state.death_dealt: Fraction of responsibility this ant contributed to killing other ants (e.g., if 2 ants killed an enemy an, each would have death_dealt=1/2
            reward_state.hill_razed: 
            reward_state.hill_distance: Fraction, 1/x
        """
        
        print ":::::Reward Info::::"
        print "food_eaten: "+str(reward_state.food_eaten)
        print "was_killed: "+str(reward_state.was_killed)
        print "death_dealt: "+str(reward_state.death_dealt)
        print "hill_razed: "+str(reward_state.razed_hill)
        print "hill_distance: "+str(reward_state.hill_distance)
        print "::::::::::::::::::::"
        
        reward = 0
        reward += LIVING_REWARD
        reward += FOOD_REWARD*reward_state.food_eaten
        reward += DEATH_REWARD*reward_state.was_killed
        reward += KILL_REWARD*reward_state.death_dealt;
        reward += RAZED_REWARD*reward_state.razed_hill;
        return reward
        
    def set_pathfinder(self, pathfinder):
        self.pathfinder = pathfinder
    
    
    def avoid_collisions(self):
        """ 
        Simple logic to avoid collisions.  No need to touch this function.
        """
        next_locations = {}
        for ant in self.world.ants:
            if ant.status == AntStatus.ALIVE:
                # Basic collision detection: don't land on the same square as another friendly ant.
                nextpos = self.world.next_position(ant.location, ant.direction) 
                if nextpos in next_locations.keys():  
                    ant.direction = 'halt'
                else:
                    next_locations[nextpos] = ant.ant_id
                        
    def do_turn(self):
        """
        do_turn just does some bookkeeping and calls the update+explore/exploit 
        loop for each living or just killed ant.  You shouldn't need to modify 
        this function.
        """
        
        # Grid lookup resolution: size 10 squares
        if self.state == None:
            fog = int(math.sqrt(self.world.viewradius2))
            self.state = GlobalState(self.world, visited_resolution=fog, resolution=fog)
        else:
            self.state.update()
            
        # explore or exploit and update values for every ant that's alive or was just killed
        for ant in self.world.ants:
            if ant.status == AntStatus.ALIVE or ant.previous_reward_events.was_killed:
                ant.direction = self.explore_and_exploit(ant)

        self.avoid_collisions()
        
        
        # record features for action taken so we can update when we arrive in the next state next turn
        for ant in self.world.ants:    
            ant.prev_features = self.features.extract(self.world, self.state, ant.location, ant.direction)
            ant.prev_value = self.value(self.state,ant.location,ant.direction)

    def update_weights(self,alpha,discount,reward,maxval,prevval,features):
        """
            Perform an update of the weights here according to the Q-learning
            weight update rule described in the homework handout.
        """
        for i in range(len(self.weights)):
            self.weights[i] += alpha*(reward + discount*maxval - prevval)*features[i]
        

    def explore_and_exploit(self,ant):
        '''
        Update weights and decide whether to explore or exploit here.  Where all the magic happens.
        YOUR CODE HERE
        '''

        actions = self.world.get_passable_directions(ant.location, AIM.keys())
        random.shuffle(actions)
        
        if len(actions)==0:
            return 'halt'
        # if we have a newborn baby ant, init its rewards and quality fcns
        if 'prev_value' not in ant.__dict__:
            ant.prev_value = 0
            ant.previous_reward_events = RewardEvents()
            ant.prev_features = self.features.extract(self.world, self.state, ant.location, actions[0])
            return actions[0]
        # step 1, update Q(s,a) based on going from last state, taking
        # the action issued last round, and getting to current state
        R = self.get_reward(ant.previous_reward_events)
        
        # step size.  it's good to make this inversely proportional to the
        # number of features, so you don't bounce out of the bowl we're trying
        # to descend via gradient descent
        alpha = float(1) / (len(ant.prev_features)*ALPHA_DIVIDER)
        # totally greedy default value, future rewards count for nothing, do not want
        discount = DISCOUNT
        
        # should be max_a' Q(s',a'), where right now we are in state s' and the
        # previous state was s.  You can use
        # self.value(self.state,ant.location,action) here
        max_next_value = 0
        max_next_action = 'halt'
        for action in actions:
            val = self.value(self.state,ant.location,action)
            if max_next_value < val:
                max_next_value = val
                max_next_action = action
        
        # should be argmax_a' Q(s',a')
        #max_next_action = 'halt'
        
        # now that we have all the quantities needed, adjust the weights
        self.update_weights(alpha,discount,R,max_next_value,ant.prev_value,ant.prev_features)

                
        # step 2, explore or exploit? you should replace decide_to_explore with
        # something sensible based on the number of games played so far, self.ngames
        
        if self.ngames < EXPLORE_THRESHOLD:
            decide_to_explore = True
        else:
            if random.randint(0,(self.ngames-EXPLORE_THRESHOLD)/2) == 0:
                decide_to_explore = True
            else:
                decide_to_explore = False
            decide_to_explore = False
        if decide_to_explore:
            return actions[0]
        else:      
            return max_next_action
        



# Set BOT variable to be compatible with rungame.py                            
BOT = ValueBot


    

def run(arg):
    start_time = time.time()
    
    game_number = int(arg[1])
    
    #    PLAY_TYPE = 'step'
    #  PLAY_TYPE = 'batch'
    #  PLAY_TYPE = 'play'
    
    # Run the local debugger
    engine = LocalEngine(game=None)
    
    if game_number > 0:
        qbot = QLearnBot(engine.GetWorld(), load_file='saved_bots/qbot.json')
    else:
        # init qbot with weights 0
        qbot = QLearnBot(engine.GetWorld(), load_file=None)
        qbot.set_features(CompositingFeatures(AdvancedFeatures(), AdvancedFeatures()))
        qbot.set_weights([0 for j in range (0, qbot.features.num_features())])
        
    # Generate and play on random 30 x 30 map
    random_map = SymmetricMap(min_dim=50, max_dim=50)
    random_map.random_walk_map()
    fp = file("src/maps/2player/my_random.map", "w")
    fp.write(random_map.map_text())
    fp.close()
        
    # set up a game between current qbot and GreedyBot
    engine.AddBot(qbot)        
    engine.AddBot(GreedyBot(engine.GetWorld()))
    qbot.ngames = game_number + 1
    
    engine.Run(PLAY_TYPE, arg + ["--run", "-m", "src/maps/2player/my_random.map"])
    qbot.save('saved_bots/qbot.json')
    # this is an easy way to look at the weights
    #qbot.save_readable('saved_bots/qbot-game-%d.txt' % game_number)
        
    end_time = time.time()
    print 'training done, delta time = ', end_time-start_time
    
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Missing argument ---'
        print 'Usage: python qlearner.py <game number>'
        sys.exit()
    run(sys.argv)    