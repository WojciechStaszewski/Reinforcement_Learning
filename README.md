# Reinforcement_Learning

Tic_Tac_Toe:

General:
An AI learning to play Tic_Tac_Toe from the experience. After ca. 10000 games the AI is playing really well and if trained further becomes unbeatable. The AI plays against its counterpart and saves the learning progress in excel files 1.xlsx and 2.xlsx. If wanted the AI can read from the existing files and thus immediately become trained and ready for testing. The excel files attached contain examples of unbeatable AI. There is a module allowing a human player to test the AI skills in a game PvE mode. Alternatively, you can just display up to 10 consecutive runs of AI vs AI matches and see each step of these games for yourself.

Concepts:
The AI learning process is based on decaying epsilon-greedy concept along with unconventional reward system for effective defense.

Possible next steps:
Use symmetry to minimize amount of board states i.e. force the AI to rotate the board so that there are only 3 possible starting positions.


My_grid_world:

General:
A game of gridworld is a simple board with obstacles, startpoint, and 3 possible ends, win if the AI reaches winning point, lose if reaches losing point, lose if too many moves are made. To allow changing of board size, the weights, and policies are enforced to be in forms of the matrixes at all times. Game is created to show different types of RL based AI and easily test them in a simple environment. Afterwards, increasing the difficulty and size of the environment should be possible to further check the AI adapting possibilities.
Loading bots is just to check their final behavior, teaching new ones is fast.

Ready concepts:
The AI learning process is based on decaying epsilon-greedy concept.

TODO: 
Bots with penalty for each step;
Randomize start point bots for faster policy assessment;
Check scalability of board and create a harder environment, change conditions, e.g. add the wind.
