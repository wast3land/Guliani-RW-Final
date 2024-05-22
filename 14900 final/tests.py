#test code for item spawn probabilities
import global_variables
import shopkeep

iteration_size = 1000

player_level = 10

global_variables.PLAYER.set_level(10)

for i in range (iteration_size):
    global_variables.restock_the_shop()

for i in shopkeep.STATS:
    print(f"{i}: {int(shopkeep.STATS[i]/(len(global_variables.BLACKSMITH._forge_list)*iteration_size) * 100)}%")
    print('')