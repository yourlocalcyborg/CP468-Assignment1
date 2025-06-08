#!/usr/bin/env python3
import heapq

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
    
    def copy(self):
        return State(self.state.copy())

    def __eq__(self, other):
        if not isinstance(other, State):
            return NotImplemented
        return self.state == other.state
   
    def __lt__(self, other):
        return tuple(self.state) < tuple(other.state)


    # hash function implemented for heap
    def __hash__(self):
        return hash(tuple(self.state))

    # prints state to terminal
    def print_state(self):
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
    @staticmethod
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
    @staticmethod
    def calc_manhattan_dist(tile, target):
        tilepos = divmod(tile, 3)
        targetpos = divmod(target, 3)
        dist = (tilepos[0] - targetpos[0], tilepos[1] - targetpos[1])
        return abs(dist[0]) + abs(dist[1])

    # sum of all tiles to targets
    # a.k.a. h_2
    # inputs: current state, target state
    # returns: sum of all manhattan distances
    @staticmethod
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
    @staticmethod
    def num_misplaced_tiles(tiles, targets):
        tileslist = tiles.state
        targetslist = targets.state

        total = 0
        for i in range(0,9):
            if tileslist[i] != targetslist[i] and tileslist[i] != 0:
                total += 1

        return total

    # A* search
    # Finds lowest f(n) = g(n) + h(n) (where g(n) is the step cost from start, and h(n) is the heuristic cost to goal state),
    # expands lowest cost unexpanded node, and repeats until solution is found. 
    # inputs: target state to search for, h(n) heuristic function
    # returns: solution, number of steps to find solution, number of nodes expanded
    def a_star(self, target_state, h_n):
        open_set = [(h_n(self, target_state), 0, self)]
        g_scores = {self: 0}
        came_from = {}
        closed_set = set()
        
        nodes_expanded = 0

        while open_set:
            current_f, current_g, current_state = heapq.heappop(open_set)
            
            if current_state in closed_set:
                continue

            if current_state == target_state:
                path = []
                state = current_state
                while state in came_from:
                    path.append(state)
                    state = came_from[state] 
                path.append(self)
                path.reverse()
                
                return path, len(path) - 1, nodes_expanded
            
            closed_set.add(current_state)
            nodes_expanded += 1
            
            for neighbour in current_state.get_neighbours():
                if neighbour in closed_set:
                    continue
            
                tentative_g = current_g + 1

                if neighbour not in g_scores or tentative_g < g_scores[neighbour]:
                    came_from[neighbour] = current_state
                    g_scores[neighbour] = tentative_g
                    
                    f_score = tentative_g + h_n(neighbour, target_state)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbour))

        return None, 0, nodes_expanded

init_list = [7, 2, 4, 5, 0, 6, 8, 3, 1]

goal_list = [0, 1, 2, 3, 4, 5, 6, 7, 8]

current_state = State(init_list)
target_state = State(goal_list)
print("test printing")
current_state.print_state()

print("test neighbours")
for i in current_state.get_neighbours():
    i.print_state()

print("test manhattan distance")
print("dist from (0,0) to (0,1):", State.calc_manhattan_dist(0, 3), "(1)")
print("dist from (0,0) to (1,1):", State.calc_manhattan_dist(0, 4), "(2)")
print("dist from (2,2) to (0,1):", State.calc_manhattan_dist(8, 3), "(3)")
print("dist from (2,2) to (0,0):", State.calc_manhattan_dist(8, 0), "(4)")
print("")

print("test sum manhattan distances\n")
print("sum of\n")
current_state.print_state()
print("distances to\n")
target_state.print_state()
print("equals", State.sum_manhattan_dists(current_state, target_state), "\n")

print("test misplaced tiles")
print("using init and target as previous,", State.num_misplaced_tiles(current_state, target_state), "(8)\n")
print("using")
new_state = State([0,1,3,2,5,6,8,7,4])
new_state.print_state()
print("and target as previous,", State.num_misplaced_tiles(new_state, target_state), "(6)")
print("")

print("test eq")
print(target_state == current_state)
print(target_state == target_state)
print(target_state == target_state.copy())
print("")

print("test A*")
print("solution with h_1:")
soln, soln_steps, nodes_expanded = current_state.a_star(target_state, State.num_misplaced_tiles)
for i in soln:
    i.print_state()
print("steps:", soln_steps)
print("nodes_expanded:", nodes_expanded)

print("solution with h_2:")
soln, soln_steps, nodes_expanded = current_state.a_star(target_state, State.sum_manhattan_dists)
for i in soln:
    i.print_state()
print("steps:", soln_steps)
print("nodes_expanded:", nodes_expanded)
