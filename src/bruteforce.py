
def brute_aux(timeslots,rides):
    if rides.empty(): return (0,[])
    best = (float('inf'),[])
    ts = timeslots.pop()
    for i,ride in enumerate(rides):
        c,tt = brute_aux(timeslots,rides[:i]+rides[i+1:])
        c += cost_ride(ride,ts)
        if c < best[0]:
            best = (c,[ts])
    return best

def bruteforce(timeslots,rides):
    return brute_aux(timeslots,rides)
    
