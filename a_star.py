#!/usr/bin/env python3
import heapq
import random as r

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

    def __str__(self):
        statestr = ""
        for i in range(0, 3):
            for j in range(0, 3):
                statestr += str(self.state[i*3 + j])
            statestr += '\n'
        return statestr

    def __eq__(self, other):
        if not isinstance(other, State):
            return NotImplemented
        return self.state == other.state
   
    def __lt__(self, other):
        return tuple(self.state) < tuple(other.state)


    # hash function implemented for heap
    def __hash__(self):
        return hash(tuple(self.state))

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


    # number of mismatched tiles with other state
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
        total = 0
        for i in range(0, 9):
            # ignore calculating dist for empty tile
            if tiles.state[i] != 0:
                # get tile number, then find same tilenumber's index in target
                total += State.calc_manhattan_dist(i, targets.state.index(tiles.state[i]))
        return total

    # Linear conflicts heuristic
    # a.k.a. h_3
    # https://youtu.be/8t3lPD2Qtao
    # https://algorithmsinsight.wordpress.com/graph-theory-2/a-star-in-general/implementing-a-star-to-solve-n-puzzle/ (section on "Linear Conflict + Manhattan Distance/Taxicab geometry")
    @staticmethod
    def linear_conflicts(tiles, targets):
        def count_conflicts_line(current_state, target_state, line_positions):
            tiles_in_line = []
            for pos in line_positions:
                tile = current_state[pos]
                if tile != 0:
                    target_pos = target_state.index(tile)
                    if target_pos in line_positions:
                        tiles_in_line.append((tile, pos, target_pos))

            conflicts = 0
            for i in range(len(tiles_in_line)):
                for j in range(i + 1, len(tiles_in_line)):
                    tile1, pos1, target1 = tiles_in_line[i]
                    tile2, pos2, target2 = tiles_in_line[j]
                    if (pos1 < pos2) != (target1 < target2):
                        conflicts += 1
            return conflicts

        total = 0

        for row in range(3):
            total += count_conflicts_line(tiles.state, targets.state, [row * 3 + i for i in range(3)])

        for col in range(3):
            total += count_conflicts_line(tiles.state, targets.state, [i * 3 + col for i in range(3)])
            
            
        return total*2 + State.sum_manhattan_dists(tiles, targets)

    # Counts inversions to determine if the puzzle state is solvable.
    # For each tile, it counts how many tiles after it are smaller,
    # then if the number of total inversions are even, it is solvable.
    def is_solvable(self):
        puzzle = [t for t in self.state if t != 0]
        inversions = 0
        for i in range(len(puzzle)):
            for j in range(i + 1, len(puzzle)):
                if puzzle[i] > puzzle[j]:
                    inversions += 1
        return inversions % 2 == 0

    # A* search
    # Finds lowest f(n) = g(n) + h(n) (where g(n) is the step cost from start, and h(n) is the heuristic cost to goal state),
    # expands lowest cost unexpanded node, and repeats until solution is found. 
    # inputs: target state to search for, h(n) heuristic function
    # returns: solution, number of steps to find solution, number of nodes expanded
    def a_star(self, target_state, h_n):
        # set of discovered nodes that may be expanded
        open_set = [(h_n(self, target_state), 0, self)]

        # for node n, came_from[n] is the node preceding it on the lowest cost path from start
        came_from = {}
        
        # nodes already expanded, can ignore
        closed_set = set()
        
        # g_score[n] is currently known cost of cheapest path from start to n
        g_scores = {self: 0}

        nodes_expanded = 0

        while open_set:
            # gets state with lowest f_score
            current_f, current_g, current_state = heapq.heappop(open_set)
            
            # skip if node already expanded
            if current_state in closed_set:
                continue

            # check if goal reached, return path if so
            if current_state == target_state:
                path = []
                state = current_state
                # backtrack through came_from to figure out path to goal
                while state in came_from:
                    path.append(state)
                    state = came_from[state] 
                path.append(self)
                path.reverse()
                
                return path, len(path) - 1, nodes_expanded
            
            # mark node as expanded
            closed_set.add(current_state)
            nodes_expanded += 1
           
            # check if we've just found a better path to any neighbours
            for neighbour in current_state.get_neighbours():
                if neighbour in closed_set:
                    continue
            
                tentative_g = current_g + 1

                # save g_score for neighbour if we have a better one or one doesn't exist yet
                if neighbour not in g_scores or tentative_g < g_scores[neighbour]:
                    came_from[neighbour] = current_state
                    g_scores[neighbour] = tentative_g
                    
                    f_score = tentative_g + h_n(neighbour, target_state)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbour))

        # return None if no solution is found
        return None, 0, nodes_expanded

init_list = [7, 2, 4, 5, 0, 6, 8, 3, 1]

goal_list = [0, 1, 2, 3, 4, 5, 6, 7, 8]

current_state = State(init_list)
target_state = State(goal_list)
print("test printing")
print(current_state)

print("test neighbours")
for i in current_state.get_neighbours():
    print(i)

print("test manhattan distance")
print("dist from (0,0) to (0,1):", State.calc_manhattan_dist(0, 3), "(1)")
print("dist from (0,0) to (1,1):", State.calc_manhattan_dist(0, 4), "(2)")
print("dist from (2,2) to (0,1):", State.calc_manhattan_dist(8, 3), "(3)")
print("dist from (2,2) to (0,0):", State.calc_manhattan_dist(8, 0), "(4)")
print("")

print("test sum manhattan distances\n")
print("sum of\n")
print(current_state)
print("distances to\n")
print(target_state)
print("equals", State.sum_manhattan_dists(current_state, target_state), "\n")

print("test misplaced tiles")
print("using init and target as previous,", State.num_misplaced_tiles(current_state, target_state), "(8)\n")
print("using")
new_state = State([0,1,3,2,5,6,8,7,4])
print(new_state)
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
    print(i)
print("steps:", soln_steps)
print("nodes_expanded:", nodes_expanded)
print("")

print("solution with h_2:")
soln, soln_steps, nodes_expanded = current_state.a_star(target_state, State.sum_manhattan_dists)
for i in soln:
    print(i)
print("steps:", soln_steps)
print("nodes_expanded:", nodes_expanded)
print("")

print("solution with h_3:")
soln, soln_steps, nodes_expanded = current_state.a_star(target_state, State.linear_conflicts)
for i in soln:
    print(i)
print("steps:", soln_steps)
print("nodes_expanded:", nodes_expanded)
print("")

print("Generate 100 random puzzles to solve")
num_generations = 100
states = []
print("| #   | State                       | h1 steps | h1 exp. nodes | h2 steps | h2 exp. nodes | h3 steps | h3 exp. nodes |")
print("|-----|-----------------------------|----------|---------------|----------|---------------|----------|---------------|")
for i in range(num_generations):
    statelist = [0,1,2,3,4,5,6,7,8]
    state = State(statelist)
    r.shuffle(state.state)
    while (not state.is_solvable()) or (state in states):
        r.shuffle(state.state)        
    states.append(state)
    h1_results = state.a_star(State([0,1,2,3,4,5,6,7,8]), State.num_misplaced_tiles)
    h2_results = state.a_star(State([0,1,2,3,4,5,6,7,8]), State.sum_manhattan_dists)
    h3_results = state.a_star(State([0,1,2,3,4,5,6,7,8]), State.linear_conflicts)
    print(f"| {i+1:3} | {state.state} | {h1_results[1]:8} | {h1_results[2]:13} | {h1_results[1]:8} | {h2_results[2]:13} | {h3_results[1]:8} | {h3_results[2]:13} |")
