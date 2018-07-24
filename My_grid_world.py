# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 16:32:19 2018

@author: Wojtek

A game ofgridworld is a simple board with obstacles, startpoint, and 3 possible 
ends, win if the AI reaches winningpoint, lose if reaches losing point, lose
if too many moves are made.
To allow chaning of board size, the wieghts, and policies are enfroced to be in
forms of the matrixes at all times.
Loading bots is just to check their final beahvior, teaching new ones is fast.

LOG:
Random and TicTac bots ready
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
from os.path import isfile, join
from os import listdir
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')#'%(asctime)s:%(levelname)s:%(message)s')


class Environment:
    """Objects are tied to environment parameters, change is possible, but
        bewatch the object on board"""
    def __init__(self, board_len=4, board_wid=3):
        self.len = board_len
        self.wid = board_wid
        self.board = pd.DataFrame(np.zeros((self.wid, self.len)))
        self.init_base_obj()
        self.terminal = False
        
    def init_base_obj(self):
        win = object_on_board(3, 0 , 1, "win")
        lose = object_on_board(3, 1 , -1, "lose")
        obst = object_on_board(1, 1 , "X", "obstacle")
        for i in (win, lose, obst):
             self.add_obj(i)

    def add_obj(self, obj):
        self.board.loc[obj.row, obj.col] = obj.value

    def remove_obj(self, obj):
        self.board.loc[obj.row, obj.col] = 0
               
    def possible_moves(self, place):
        # returns list of possible moves in list of [col, row] lists
        list_of_options=[]
        for i in [-1, 1]:
            for j in [0,1]:
                vec=place.copy()
                vec[j]=vec[j]+i
                if vec[j] < self.board.shape[1-j]:
                    if vec[j] > -1:
                        if not self.board.loc[vec[1]][vec[0]] == 'X':
                            list_of_options.append(vec)
        return(list_of_options)
        
class object_on_board:
    """Add wining / losing points or obstacles"""
    
    def __init__(self, col, row, value, name=0): #wr = win rate
        self.col = col
        self.row = row
        self.value = value
        self.name = name
        
class Agent:
    """ Create AI to play the game, possible strategies:
        "nsmart" == random movement
        "TT_bot" == behaves as TicTacToe bot I created before, i.e. plays randomly 
                    with itselfto learn, uses a decaying epsilon greedy strategy
                    This bot can fall in infinite loop if not for a 
                    max-in-game-movement-limit
        "StepAI" == introducing a penalty for every step above min(5) taken. TODO"""
    
    epsilon_greedy=0.01
    
    def __init__(self,env, start_position=[0,2], strategy="nsmart", load=False):
        
        self.AI_pawn = object_on_board(start_position[0],
                                       start_position[1],
                                       "AI", "AI_pawn")
        self.start_position = start_position 
        self.curr_position = self.start_position
        self.strategy = strategy
        
        if not load:
            self.value_board = env.board.copy()
            self.value_board_weights = pd.DataFrame(np.zeros((env.wid, env.len)))
            logging.info("Creating a new AI")   
        else:
            self.load_value_board()
            self.epsilon_greedy = 0.000000001
            logging.info("AI loaded")                        

        env.add_obj(self.AI_pawn)        
        

    def pick_a_move(self, env):
        options = env.possible_moves(self.curr_position)
        if self.strategy == "nsmart":
            movement_choice = options[np.random.choice(len(options))]
        elif self.strategy == "TT_bot":
            if self.epsilon_greedy>np.random.uniform(0,1):
                movement_choice = options[np.random.choice(len(options))]
            else:
                best = -5
                for i in options:
                    value = self.value_board.loc[i[1]][i[0]]
                    try:
                        if value>best:
                            best = value
                            movement_choice = i
                    except TypeError:
                        print("LOST")
                        raise

        return (movement_choice)


    def execute_move(self, env, new_position):
        
        env.remove_obj(self.AI_pawn)
        self.AI_pawn.col = new_position[0]
        self.AI_pawn.row = new_position[1]
        env.add_obj(self.AI_pawn)
        self.curr_position = new_position
        if new_position == [3,0]:
            env.terminal = 1
        elif new_position == [3,1]:
            env.terminal = -1         

    def update_value_board(self, positions, game_result): # strategy and conditions dependent
        
        for cell in positions:
            col = cell[0]
            row = cell[1]
            w = self.value_board_weights.loc[row, col]
            old_av = self.value_board.loc[row, col]
            new_value = (w*old_av+game_result)/(w+1)
            self.value_board.loc[row, col] = new_value
            self.value_board_weights.loc[row, col] = w+1
      
            logging.debug("updated value board {}, updated weights board {}"
                         .format(self.value_board, self.value_board_weights))

    def load_value_board(self): # strategy and board-size dependent
        path = os.path.dirname(os.path.abspath(__file__))+"//"
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
        logging.debug(onlyfiles) 
        
        name = self.strategy + ".xlsx"
        if name in onlyfiles:
            self.value_board = pd.read_excel(path+name, sheet_name='value_board')
            self.value_board_weights = pd.read_excel(path+name, sheet_name='value_board_weights')            

        logging.debug(self.value_board)
        logging.debug(self.value_board_weights)
        
    def save_value_board(self): # strategy and board-size dependent
        
        path = os.path.dirname(os.path.abspath(__file__))+"//"
        path = path + self.strategy
        
        writer = pd.ExcelWriter(path + ".xlsx")
        self.value_board.to_excel(writer, sheet_name = 'value_board')
        self.value_board_weights.to_excel(writer, 
                                          sheet_name = 'value_board_weights')

def play_gridworld(player, env):
    
    move_number = 0
    positions=[AI.start_position]
    while env.terminal == False:
        movement_choice = player.pick_a_move(env)
        player.execute_move(env, movement_choice)
        if movement_choice not in positions:
            positions.append(movement_choice)
        move_number += 1
        if move_number>50:
            env.terminal=-1
    logging.debug("number of moves {}, reward = {}".format(move_number, env.terminal))
    if player.strategy == "TT_bot":
        player.update_value_board(positions, env.terminal)

    return(move_number, env.terminal)
            
def restart_the_game(player, env):
    if abs(env.terminal) == 1:
        player.execute_move(env, player.start_position)   
        env.terminal=False
        

if __name__ == "__main__":
    
    edu_chart = pd.DataFrame()
    strategy_line = ["TT_bot","nsmart"]
    
    start = datetime.now()  
    load_save = False
    load_AI = load_save
    save_AI = load_save
    time=[]
    s3=[]    
    for strategies in strategy_line:
        s = 0
        res_total = 0
        env=Environment()
        AI = Agent(env, strategy=strategies, load=load_AI)
        s2 = []
        res2 = []
        av_list = []
            
        for i in range(121):
            moves_amount, res = play_gridworld(AI, env)
            restart_the_game(AI, env)
            
            if i% 10 == 0:
                if not load_AI:
                    AI.epsilon_greedy = 10/(i+1)
                if i%4 == 0:
                    end = datetime.now()
                    logging.info("itereation #{}, in period of {}s"
                                 .format(i, (end - start).seconds))
                    start = datetime.now()
                    time.append(int((end - start).seconds))
                    
            s += int(moves_amount) 
            s2.append(moves_amount)                
            res_total += res  
            res2.append(res)            
            av_list.append(s/(i+1))
                        
        s3.append(s2)   

        if save_AI == True:
            AI.save_value_board()
            logging.info("AI saved")
                    
        edu_chart[strategies+"-av"] = av_list   
        
        logging.info(" for stategy {} average amount of moves is {}, and the "
                     "total result = {}". format(strategies, s/(i+1), res_total))        
        logging.info(AI.value_board)
        logging.info(AI.value_board_weights)
                
    if i >40:
        edu_chart[30:].plot()

""" 
    add some nice game view plot / movie
"""