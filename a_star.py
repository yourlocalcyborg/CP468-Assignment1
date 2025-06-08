#!/usr/bin/env python3

class State:
    state = None

    # board state is stored as a list of which tile is in what position
    # where the 0 tile is the empty space, i.e.
    # 7 2 4
    # 5 0 6
    # 8 3 1
    # would be
    # [7,2,4,5,0,6,8,3,1]
    def __init__(self, state):
        self.state = state

    # prints state to terminal
    def printstate(self):
        for i in range(0, 3):
            for j in range(0, 3):
                print(self.state[i*3 + j], end=" ")
            print("")
        print("")

    # returns: list of states of possible moves,
    # as in what state nodes are adjacent to the current node in state space 
    def get_neighbours(self):
        emptytile = self.state.index(0)
        swaptiles = State.get_tile_neighbours(emptytile)

        states = []
        for i in swaptiles:
            newstate = self.state.copy()
            newstate[emptytile], newstate[i] = newstate[i], newstate[emptytile]
            states.append(State(newstate))

        return states
        
        
    # inputs: tile index
    # returns: arrays of neighbouring tiles to tile
    def get_tile_neighbours(tile):
        # Perhaps there is a better way to calculate Manhattan neighbours but it escapes me currently
        match tile:
            case 0:
                return [1, 3]
            case 1:
                return [0, 2, 4]
            case 2:
                return [1, 5]
            case 3:
                return [0, 4, 6]
            case 4:
                return [1, 3, 5, 7]
            case 5:
                return [2, 4, 8]
            case 6:
                return [3, 7]
            case 7:
                return [4, 6, 8]
            case 8:
                return [5, 7]

    # sum of horizontal and vertical distances to target,
    # a.k.a. number of moves to move tile to target space
    # inputs: tile index, target index
    # returns: manhattan distance between tile and target space
    def calc_manhattan_dist(tile, target):
        tilepos = divmod(tile, 3)
        targetpos = divmod(target, 3)
        dist = (tilepos[0] - targetpos[0], tilepos[1] - targetpos[1])
        return abs(dist[0]) + abs(dist[1])

    # sum of all tiles to targets
    # a.k.a. h_2
    # inputs: current state, target state
    # returns: sum of all manhattan distances
    def sum_manhattan_dists(tiles, targets):
        tileslist = tiles.state
        targetslist = targets.state

        total = 0
        for i in range(0, 9):
            # ignore calculating dist for empty tile
            if tileslist[i] != 0:
                # get tile number, then find same tilenumber's index in target
                total += State.calc_manhattan_dist(i, targetslist.index(tileslist[i]))

        return total

    # a.k.a. h_1
    # inputs: current state, target state
    # returns: number of tiles of difference (not counting empty tile)
    def num_misplaced_tiles(tiles, targets):
        tileslist = tiles.state
        targetslist = targets.state

        total = 0
        for i in range(0,9):
            if tileslist[i] != targetslist[i] and tileslist[i] != 0:
                total += 1

        return total

    # should be able to write an A star function that takes a heuristic function as an argument like
    #def a_star(self, targetstate, h_n):
    # state.a_star(target, num_misplaced_tiles)

    # also shouldn't need to worry about the g(n) part because any neighbouring state will be one move.
    # unsure how to represent entire tree though, perhaps just have a visited list and an unexpanded nodes list,
    # and just search the unexpanded nodes for the lowest heuristic score.


init_list = [7, 2, 4, 5, 0, 6, 8, 3, 1]

goal_list = [0, 1, 2, 3, 4, 5, 6, 7, 8]

current_state = State(init_list)
target_state = State(goal_list)
print("test printing")
current_state.printstate()

print("test neighbours")
for i in current_state.get_neighbours():
    i.printstate()

print("test manhattan distance")
print("dist from (0,0) to (0,1):", State.calc_manhattan_dist(0, 3), "(1)")
print("dist from (0,0) to (1,1):", State.calc_manhattan_dist(0, 4), "(2)")
print("dist from (2,2) to (0,1):", State.calc_manhattan_dist(8, 3), "(3)")
print("dist from (2,2) to (0,0):", State.calc_manhattan_dist(8, 0), "(4)")
print("")

print("test sum manhattan distances\n")
print("sum of\n")
current_state.printstate()
print("distances to\n")
target_state.printstate()
print("equals", State.sum_manhattan_dists(current_state, target_state), "\n")

print("test misplaced tiles")
print("using init and target as previous,", State.num_misplaced_tiles(current_state, target_state), "(8)\n")
print("using")
new_state = State([0,1,3,2,5,6,8,7,4])
new_state.printstate()
print("and target as previous,", State.num_misplaced_tiles(new_state, target_state), "(6)")
