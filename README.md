# Quicksort: Mobility Hackathon
## organized by Valeo and Quantic

Some of the preliminary data analysis code isn't included, since we made our statistics from the command line interface,
using simply the pandas library, and we werent able to find meaningful correlations at first glance.
The data about failure prediction doesn't correlate with our current objective: ride duration prediction and optimisation. 

## quicksort
We are analysing drives to find out patterns.
We use open data from paris traffic to find out patterns in daily traffic depending on the period of the year.
We cross reference these trajectories to the traffic of Paris to compute the time wasted in traffic.
And we finally consider several reorderings to optimize those drives.

![traffic pic](heatmap.png)

## credits
- https://opendata.paris.fr
- https://github.com/astyonax/heartbeat-traffic
