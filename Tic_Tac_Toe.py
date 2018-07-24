1,1# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 15:05:55 2018

@author: Wojtek

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import xlsxwriter
from os.path import isfile, join
from os import listdir
import os 
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')#'%(asctime)s:%(levelname)s:%(message)s')


class Environment:
    
    
    dim=3
    def __init__(self):
        self.board=pd.DataFrame(np.zeros((self.dim,self.dim)))
        self.terminal=False
   
    def update(self, the_move, mock_move=False):
        move_type=the_move[0]
        col=the_move[1]
        row=the_move[2]
        self.board[col][row]=move_type
        self.win_condition(move_type)
    
    def win_condition(self, move_type):
        diag1=0
        diag2=0
        for i in range(Environment.dim):
            if (abs(self.board[i].sum()) == Environment.dim or 
                abs(self.board.iloc[i].sum()) == Environment.dim):
                self.terminal=move_type
                break            
            else:
                diag1 += self.board[i][i]
                diag2 += self.board[Environment.dim-i-1][i]
                
        if (abs(diag1) == Environment.dim or 
            abs(diag2) == Environment.dim):
            self.terminal=move_type
        
    def draw_board(self, plot_number, fig, human=False):

        ax=fig.add_subplot(self.dim, self.dim, plot_number) 
        for col in range(self.dim):
            for row in range (self.dim):
                if self.board[col][row]==1:
                     sign_type="x"
                     ax.plot([col+0.5],[2.5-row],"ko", marker=sign_type, markersize=10)
                elif self.board[col][row]==-1:
                     sign_type="o"#"$\circ$"
                     ax.plot([col+0.5],[2.5-row],"ko", marker=sign_type, markersize=10)
                     ax.plot([col+0.5],[2.5-row],"wo", marker=sign_type, markersize=8)
                     
        ax.axis([0, self.dim, 0, self.dim])
        ax.axvline(x=1, linewidth=2, color='k',)
        ax.axvline(x=2, linewidth=2, color='k',)
        ax.axhline(y=2, linewidth=2, color='k',)
        ax.axhline(y=1, linewidth=2, color='k',)
        ax.set_title('Move ' + str(plot_number))
        ax.axis('off')
        if human:
            plt.tight_layout()
            plt.show()

        elif self.terminal or plot_number==9:
            plt.tight_layout()
            plt.show()

    def is_empty(self, board):
        empty=[]
        for row in range(Environment.dim):
            for col in range(Environment.dim):
                if board[col][row]==0:
                    empty.append([col,row])
        return(empty)


class player():

    
    id = 0
    draws = 0

    def __init__(self, move_type, strategy="smart", epsilon_greedy=0.2):
        self.move_t=move_type    
        self.learning_episodes=0
        self.acc_reward=0
        self.strategy=strategy
        self.board_state_list=[]
        self.value_database={}
        self.epsilon=epsilon_greedy
        self.id = player.id + 1
        player.id += 1

    def save_weights(self, path):
        path= path + str(self.id)
        workbook = xlsxwriter.Workbook(path +'.xlsx')
        worksheet = workbook.add_worksheet('Sheet1')
        frame=pd.DataFrame(self.value_database)  
        worksheet.write(0, 0, "unique_number")
        worksheet.write(0, 1, "value")
        worksheet.write(0, 2, "weight")

        for i in range(len(self.value_database)):
            worksheet.write(i+1, 0, frame.columns[i])
            worksheet.write(i+1, 1, frame[frame.columns[i]][0])
            worksheet.write(i+1, 2, frame[frame.columns[i]][1])
        workbook.close()

    def load_weights(self, pathxlsx):
        frame= pd.read_excel(pathxlsx)
        for i in range(len(frame)):
            self.value_database.update({frame["unique_number"][i]:
                                        [frame["value"][i],
                                         frame["weight"][i]]})

    def update_the_score(self, env):
        reward=env.terminal
        self.learning_episodes +=1
        if reward==self.move_t:
            self.acc_reward+= abs(reward)

        if self.strategy=="smart":
            self.update_dic(env)
        self.board_state_list=[]
        
        if self.learning_episodes%10000==0:
            self.epsilon=0.9*self.epsilon

    def update_dic(self, env):
        next_value = 0
        if env.terminal==self.move_t:
            next_value = 1
        elif env.terminal == -self.move_t:
            next_value = -1
            empty=env.is_empty(env.board)
            if len(empty)<2:
                next_value+=0.2
                if len(empty)==0:
                    next_value+=0.2
            #decrease the penalty if you defend long enough                    
            #you can defend yourself at most 3 times
            #for each defence you get a lower penalty of 0.2
        logging.debug("board_state_list {}".format(self.board_state_list))
        self.board_state_list.reverse()

        for board_states_reversed in self.board_state_list:            
            value= self.value_database.get(board_states_reversed)[0]   
            weight= self.value_database.get(board_states_reversed)[1]   
            new_weight= weight+1
            new_value=(value*weight+next_value)/new_weight
            self.value_database.update({board_states_reversed: [new_value, new_weight]})
            next_value=new_value
            logging.debug("update_dic: {}".format(new_value))
            
    def move(self, env):
        empty=env.is_empty(env.board)
        which_from_empty=np.random.choice((len(empty)))    
          
        if self.strategy == "smart" and len(empty)>1:
            if self.epsilon<np.random.uniform(0,1):
                highest_value = -1
                list_value = []
                for i in range(len(empty)):
                    col = empty[i][0]
                    row = empty[i][1]
                    value, unique_number = self.get_value(env.board, col, row)
                    if value>highest_value:
                        if not (value == highest_value and 0.5 > np.random.uniform(0,1)):
                            highest_value = value
                            which_from_empty = i
                    list_value.append(highest_value)
                        

        col=empty[which_from_empty][0]
        row=empty[which_from_empty][1]  
        
        if  self.strategy == "smart" and len(empty)>1:
            
            value, unique_number = self.get_value(env.board, col, row)
            move_matrix = pd.DataFrame(np.zeros((Environment.dim, Environment.dim)))
            move_matrix[col][row] = self.move_t
            new_board_state = env.board + move_matrix
            self.board_state_list.append(self.get_unique_number(new_board_state))        

        the_move = [self.move_t , col,  row]                  
        return(the_move)
        
    def get_value(self, board, col, row):
        
        mock_board=pd.DataFrame()
        mock_board=mock_board.append(board)
        mock_board[col][row]=self.move_t
        unique_number=self.get_unique_number(mock_board)
        if self.value_database.get(unique_number):
            value= self.value_database.get(unique_number)[0]
        else:
            value= self.initialize_value(mock_board)
            weight=1
            self.value_database.update({unique_number:[value, weight]})               
            logging.debug("dic_creatd, {}".format(self.value_database))

            
        return (value, unique_number)        
    
    def get_unique_number(self, board):
        
        unique_number=0
        digit=0                
        multiplier=0
        for col in range(len(board)):
            for row in range (len(board)):                

                if board[col][row]==0:
                    digit=0
                elif board[col][row]==1:
                    digit=1
                else:
                    digit=2
                #logging.debug("col = {}, row={}, digit={}, multiplier={}".format(col, row, digit, multiplier))
                unique_number += digit*len(board)**multiplier
                multiplier +=1
                
        return (unique_number)
            
    def initialize_value(self, predictied_board):
        
        diag1 = 0
        diag2 = 0
        initial_expected_value = 0  
        for i in range(Environment.dim):
            if (abs(predictied_board[i].sum()) == Environment.dim or 
                abs(predictied_board.iloc[i].sum()) == Environment.dim):
                initial_expected_value = 1                    
                break            
            else:
                diag1 += predictied_board[i][i]
                diag2 += predictied_board[Environment.dim-i-1][i]
                
        if (abs(diag1) == Environment.dim or
            abs(diag2) == Environment.dim):
                initial_expected_value=1          
                        
        return(initial_expected_value)               


class Human_player():
    
    
    def __init__(self, move_type, strategy=0):
        self.move_t=move_type    
        self.learning_episodes=0
        self.acc_reward=0
        if self.move_t == 1: 
            self.sign_type ="X"
        else:
            self.sign_type ="O"
        
    def update_the_score(self, env):
        reward=env.terminal
        self.learning_episodes +=1
        if reward==self.move_t:
            self.acc_reward+= abs(reward)
            
    def move(self, env):
        
        plt.figure()
        plt.close()
        self.draw_a_board(env.board)
        print(env.board.replace([1,-1,0],["X","O","#"]))
        
        while True:
            move = input("Enter coordinates col, row for your next move (col, row=1..3): ")
            col, row = move.split(',')
            col = int(col)-1
            row = int(row)-1
            if col in [0, 1, 2] and row in [0, 1, 2]:
                if env.board[col][row]==0:
                    print("Data accepted")
                    return(self.move_t, col, row)
                else:
                    print("This place is not available, try again")
            else:
                print("Data out of range, try again")
                
    def draw_a_board(self, board):
        

        plt.figure() 
        plt.ion()
        for col in range(Environment.dim):
            for row in range (Environment.dim):

                if board[col][row] == 1:
                     sign_type ="x"
                     plt.plot([col+0.5],[2.5-row],"ko", marker=sign_type, markersize = 30)
                elif board[col][row] == -1:
                     sign_type ="o"
                     plt.plot([col+0.5],[2.5-row],"ko", marker=sign_type, markersize = 30)
                     plt.plot([col+0.5],[2.5-row],"wo", marker=sign_type, markersize = 28)             
        plt.axis([0, 3, 0, 3])
        plt.axvline(x=1, linewidth=2, color='k',)
        plt.axvline(x=2, linewidth=2, color='k',)
        plt.axhline(y=2, linewidth=2, color='k',)
        plt.axhline(y=1, linewidth=2, color='k',)
        plt.axis('off')
        plt.title("Human player sign is {}".format(self.sign_type))
        plt.pause(0.01)
        plt.show()
        
def play_a_game(p1, p2, drawing=False, current_player=1):

    
    env = Environment()
    players=[p1, p2]
    human = "Human" in str(players)
    if drawing and not human:
        fig=plt.figure()    

    
    for i in range(Environment.dim**2):
        current_player=1-current_player
        the_move=players[current_player].move(env)
        env.update(the_move)        
    
        if drawing and not human:
            env.draw_board(i+1, fig, human)  
                
        if env.terminal:
            logging.debug("The winner is {} after {} moves".format( env.terminal, i+1))            
            break
        else:
            if i==8:
                env.terminal=0
                player.draws+=1
                
    p1.update_the_score(env)
    p2.update_the_score(env)
    return(env)


def trigger_the_game(p1, p2, drawing=True, number_of_episodes=10):


    if number_of_episodes > 10:
        drawing = False
    log_data_for_last_1000_games = True
    if log_data_for_last_1000_games:            
        old_reward_sum = p1.acc_reward + p2.acc_reward
        draws_old = player.draws
        last_1000_diff = []
        
    for i in range(number_of_episodes):
        current_player=i%2
        env=play_a_game(p1, p2, drawing, current_player)
    
        if (i+1)%1000 == 0:
            logging.info("Game number = {}".format(i))            
            if log_data_for_last_1000_games:         
                new_reward_sum = p1.acc_reward + p2.acc_reward
                diff = new_reward_sum-old_reward_sum
                draws_new = player.draws
                diff_draws = draws_new - draws_old
                last_1000_diff.append([diff, diff_draws])
                x = [p1.acc_reward/p1.learning_episodes, 
                     p2.acc_reward/p1.learning_episodes, 
                     (p1.acc_reward+p2.acc_reward)/p1.learning_episodes]                
                logging.info("wins {} and draws {} in last 10000 games".format(diff, diff_draws))
                logging.info("p1 winrate {}, p2 winrate {}, acc_winrate {}".format(x[0], x[1], x[2]))
                old_reward_sum = new_reward_sum 
                draws_old = draws_new  
            
    return(p1, p2, env) #, win_rate_list)#, last_1000_diff)   
    
    
    
if __name__ == "__main__":  
    
    
    use_database = True
    learning=False
    human_check=0

    if learning:
        epsilon = 0.2
    else:
        epsilon = 0.001
        
    if not "p1" in locals():
        p1 = player(1, strategy = "smart", epsilon_greedy = epsilon)
        p2 = player(-1, strategy = "smart", epsilon_greedy = epsilon) 
        
    if use_database: #adjust the path to where your computer
        path = os.path.dirname(os.path.abspath(__file__))+"//"#[:-12]+ "//" #"machine_learning_examples//TIC_TAC_BOTS//"
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
        logging.debug(onlyfiles)
        id_xlsx = "1.xlsx"
        if id_xlsx in onlyfiles: 
            p1.load_weights(path + id_xlsx)
            logging.info("Database loaded: player 1")
        else:
            logging.warning("Database not found: player 1")
        id_xlsx = "2.xlsx"           
        if not human_check:
            if id_xlsx in onlyfiles:
                p2.load_weights(path + id_xlsx)
                logging.info("Database loaded: player 2")
            else:
                logging.warning("Database not found: player 2")
    
    hours=1
    if learning:        
        hours=7
        episodes=80000 #80000 episodes/hour is pace on my machine
    elif not human_check:
        episodes=10

    else:
        p2 = Human_player(-1)
        episodes=2
        
    for i in range(hours): 
        start = datetime.now()
        p1, p2, env = trigger_the_game(p1, p2, number_of_episodes = episodes)
        logging.info("rewards p1 {}, rewards p2 {}, all_episodes {}, draws:".format(p1.acc_reward, p2.acc_reward, p1.learning_episodes, player.draws))
        end = datetime.now()
        logging.info("Runtime: {}s".format( (end - start).seconds))

    if learning:
        p1.save_weights(path)
        p2.save_weights(path)
        logging.info("database updated")
        
"""
    TODO:?
            descriptions, cleanup, repeat last
            human palyer
        both players acting as one?
"""





