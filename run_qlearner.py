#!/usr/bin/env python
import qlearner

# Loop qlearner, feeding in a new game number each iteration.
num_games = 50
command = "python qlearner.py"
for i in range(num_games):
    qlearner.run(["D:\\UPENN\\CIS 99\\Project\\final_proj\\qlearner.py", str(i)])

