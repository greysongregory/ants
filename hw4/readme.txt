LIVING_REWARD = -1
FOOD_REWARD = 19
DEATH_REWARD = -4
KILL_REWARD = 14
EXPLORE_THRESHOLD = 10
ALPHA_DIVIDER = 5
DISCOUNT = .6

Above are the constants I used in my program. 
alpha = float(1) / (len(ant.prev_features)*ALPHA_DIVIDER), inversely proportional with a divider to make it even smaller
discount is .6 as obove
reward function = 
reward = 0
reward += LIVING_REWARD
reward += FOOD_REWARD*reward_state.food_eaten
reward += DEATH_REWARD*died
reward += KILL_REWARD*reward_state.death_dealt;
where died is whether or not you died (0 or 1)

Finding the right weights was extremely tricky, so I focused mostly on that and used the existing features, many of which I had also implemented in HW3.
Most favored: Friendly adjacent+Closest enemy 2 away
Least favored: Closest food > 4 away+Closest enemy 1 away

My exploration strategy is always explore while #games<EXPLORE_THRESHOLD and then random explore/exploit after that, where the chance of exploiting increases with # games.

After much much trial and error, I found the key to beating greedybot! I found that greedybot always won because of its numbers, so I made food very unproportionately strong reward with death dealt about 90% as good. Also, I lowered my explore threshold to favor exploitation much more in later games. From my tests, Qbot wins 3/5 times