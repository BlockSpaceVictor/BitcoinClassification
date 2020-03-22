import pandas as pd 
import numpy as np 
from scipy import stats
import matplotlib.pyplot as plt 
from matplotlib import style
style.use("ggplot")
from sklearn import cluster 
from sklearn import preprocessing
from yellowbrick.cluster import KElbowVisualizer
from sklearn.cluster import KMeans

data = pd.read_csv('test.csv')

data2 =data
#print(data.info)



#print(data.head())
numeric = data2.iloc[:,1:]

x = numeric.values
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)


#print(df.head(10))

for k in range(2, 15):
	kmeans = cluster.KMeans(n_clusters=k)
	kmeans.fit(x_scaled)
	clusters = kmeans.cluster_centers_
	#print clusters 
	#print(clusters)
	y_km = kmeans.fit_predict(x_scaled)
	unique, counts = np.unique(y_km, return_counts=True)
	print(f"Cluster counts for k = {k}: ", dict(zip(unique, counts)))
	
model = KMeans()
visualizer = KElbowVisualizer(model, k=(2,15))
visualizer.fit(x_scaled)
visualizer.show()

visualizer2 = KElbowVisualizer(model, k=(2,15), metric='calinski_harabasz', timings=False)
visualizer2.fit(x_scaled)
visualizer2.show()

#print(kmeans)
#labels = kmeans.predict(df)
#print(labels)
#df_final["cluster"] = labels.tolist()
#print(df_final)


