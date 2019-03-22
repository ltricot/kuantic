
def compute_ride(abs_pos,cost_map,DLA,DLO,res):
    rel_pos = np.copy(abs_pos)
    cost = 0
    for xy in rel_pos:
        xy[0] = int(res * (xy[0]-DLA[0]) / (DLA[1]-DLA[0]))
        xy[1] = int(res * (xy[1]-DLO[0]) / (DLO[1]-DLO[0]))
        cost += cost_map[xy]

