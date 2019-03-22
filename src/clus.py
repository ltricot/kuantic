
from sklearn.cluster import KMeans

# number of clusters
bestNC = 0
bestS = float('inf')
for NC in range(1,15):
    clt = KMeans(n_clusters=NC)
    clt.fit(X)
    S = clt.score(X) * NC # custom score func
    print(f'{NC} scored {S}')
    if S < bestS:
        bestS = S
        bestNC = NC

if bestNC == 0:
    print('Something went wrong')
else:
    clt = KMeans(n_clusters=bestNC)
    y_pred = clt.fit_predict(X)
    for i in range(len(X)):
        plt.plot(X[i],c=y_pred[i])

