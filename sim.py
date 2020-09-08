#!/usr/bin/env python3

import numpy as np
from pprint import pprint

def heartbeat(x):
    y = np.copy(x)
    y[np.logical_and(x >= 0, x <= 4)] = 0
    y[np.logical_and(x >= 4, x <= 8)] = (y[np.logical_and(x >= 4, x <= 8)] - 4) / 4
    y[np.logical_and(x >= 8, x <= 16)] = 1 - (y[np.logical_and(x >= 8, x <= 16)] - 8) / 4
    y[np.logical_and(x >= 16, x <= 20)] = (y[np.logical_and(x >= 16, x <= 20)] - 16) / 4 - 1
    y[np.logical_and(x >= 20, x <= 24)] = 0
    return y

class FlowNetwork:
    def __init__(self, n=0):
        self.capacity = np.zeros((n,n), dtype='uint8')
        self.occupancy = np.zeros((n,n), dtype='uint8')
        self.n_vertices = n
        self.sources = dict()
        self.fflows = None
        self.unique_mapping = None

    def add_vertex(self):
        n = self.n_vertices
        self.n_vertices += 1
        self.capacity = np.append(np.append(self.capacity, np.zeros((1, n), dtype='uint8'), axis=0), np.zeros((n+1,1), dtype='uint8'), axis=1)
        self.occupancy = np.append(np.append(self.occupancy, np.zeros((1, n), dtype='uint8'), axis=0), np.zeros((n+1,1), dtype='uint8'), axis=1)
        self.flow_configuration = np.append(np.append(self.flow_configuration, np.zeros((1, n), dtype='uint8'), axis=0), np.zeros((n+1,1), dtype='uint8'), axis=1)
        return n

    def set_capacity(self, i, j, capacity):
        if i >= self.n_vertices or j >= self.n_vertices:
            raise ValueError(f'One of {(i,j)} is not a vertex')
        self.capacity[i, j] = capacity

    def set_occupancy(self, i, j, occupancy):
        if i >= self.n_vertices or j >= self.n_vertices:
            raise ValueError(f'One of {(i,j)} is not a vertex')
        self.occupancy[i, j] = occupancy

    def set_source(self, i, tiles_R=0, tiles_C=0, tiles_I=0, P_R=0, P_C=0, P_I=0):
        ttotal = 4 * (tiles_R + tiles_C + tiles_I)
        h24 = tiles_C * P_C / ttotal + tiles_I * P_I / ttotal
        self.sources.update([(i, (tiles_R * P_R / ttotal, h24 / 4))])

    def _find_all_max_st_flow(self):
        # First, we compute the traffic deltas
        if len(self.sources) < 2:
            raise ValueError("Cannot simulate a flow network with less than 2 sources")
        times = np.arange(0, 24)
        heartbeats = np.append(heartbeat(times), heartbeat(23 - times), axis=0).reshape(2, 24)
        sources = np.array([ key for key in self.sources.keys() ])
        values = np.array([ value for value in self.sources.values() ])
        # TODO: We need to preserve integrality here
        traffic_deltas = np.matmul(values, heartbeats)
        print("Traffic deltas - 24h")
        print(traffic_deltas)
        
        # Next, we find the fundamental flows
        traffic_deltas, self.unique_mapping = np.unique(traffic_deltas, axis=1, return_inverse=True)
        print("Traffic deltas - unique")
        print(traffic_deltas)
        print("Unique mapping")
        print(self.unique_mapping)
        self._push_relabel(sources, traffic_deltas)
        

    def _push_relabel(self, sources, deltas):
        """
        self.fflow is a tensor of all fundamental max-st flows
        Currently, we know there are at least 9 fundamental flows in the heartbeat function:
        0-flow: (0-4, 12, 20-23),
        1-flow: (5, 11), 2-flow: (6, 10), 3-flow: (7, 9), 4-flow: (8)
        -1-flow: (13, 19), -2-flow: (14, 18), -3-flow: (15, 17), -4-flow: (16)
        Notice that for any n-flow, the -n-flow has the exact same but negative traffic-delta.
        This is the same as switching the supersource and supersink in the graph.
        Research should be made to see if it can be made even smaller.
        Some examples of ways it could:
        - Integrality makes traffic delta the same
            + Need to compute inverse mapping of unique() at runtime
            + EDIT: This simulator is doing exactly this
        - Some proof about the interchangeability of the supersink & supersource in a graph
            + Need to prove it at runtime somehow
            + Or need to find a generalization for all graphs...
            + Would effecively find a mapping between a n-flow and a -n-flow...
        - Some nicely fundamental flows
            + A faster than Theta(|V||E|^2) algorithm to map a fundamental flow to any
              of the heartbeat flow networks
        - Some truly fundamental flows
            + A faster than Theta(|V|^3) algorithm to map a fundamental flow to any
              of the flow networks generalized by any traffic-delta function
        """
        n = self.n_vertices
        # Flow
        f = np.zeros((deltas.shape[1], n+2, n+2)) # (unique index, n+2, n+2)
        # Labels
        l = np.zeros(n+2)
        

        # Initialization
        l[1] = n + 2
        f[:,sources,:] = np.abs(deltas)
        breakpoint()
        # Excess flows
        # TODO: Set xf to the excess flows xf[u] = sum(v in V) f(v, u) - sum(v in V) f(u, v)
        xf = np.zeros(n+2)

        # Convergence
        while True:
            # TODO: Implement this
            break

    def run(self):
        populations = np.zeros((), dtype='uint8')
        self._find_all_max_st_flow()
        
        # Next, we run the simulation (for a single day)
        for hour in range(0, 24):
            pass
        return populations

if __name__ == '__main__':

    """
        We are simulating the following graph

           3    10
        A <-> B -> C
        ^     ^    ^ 
      4 |    5 \   | 3
        |       v  v
        D<-------> E
             4 

        With sources
        A: alpha_R = 1, P_R = 50
        C: alpha_C = 1, P_C = 20
        D: alpha_I = 1, P_I = 30
    
        With initial occupancy of 0 everywhere
    """
    network = FlowNetwork(n=5)
    network.set_source(0, P_R=50, tiles_R=1)
    network.set_source(2, P_C=20, tiles_C=1)
    network.set_source(3, P_I=30, tiles_I=1)

    # Numbers in the design reprensent the multiple of 24 or 12 used
    capacities = {
        (0, 1, 12), (1, 0, 12),
        (1, 2, 40),
        (1, 4, 20), (4, 1, 20),
        (2, 4, 12), (4, 2, 12),
        (3, 4, 16), (4, 3, 16),
        (4, 0, 16), (0, 4, 15)
    }
    for (i, j, c_ij) in capacities:
        network.set_capacity(i, j, c_ij)
    network.run()
