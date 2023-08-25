import pandas as pd
df = pd.read_csv('fortfft.csv')

import matplotlib.pyplot as plt
import plotly.express as px


fig = px.scatter(x=df['label'], y=df['pred'])

# fig = px.scatter(x=df['label'], y=df['pred'])
# fig.show()


import numpy as np
from sklearn.decomposition import PCA

pca = PCA(n_components=1)
pred_trans = pca.fit_transform(np.expand_dims(np.array(df['pred']), -1))
fig = px.scatter(x=df['label'], y=pred_trans)

fig.show()
# import numpy as np
# import plotly.graph_objects as go

# my_data = np.random.rand(6500,3)  # toy 3D points
# marker_data = go.Scatter3d(
#     x=df['label'], 
#     y=df['pred'], 
#     # z=df['c4'], 
#     marker=go.scatter3d.Marker(size=3), 
#     opacity=0.8, 
#     mode='markers'
# )
# fig=go.Figure(data=marker_data)
# fig.show()



#! Current plan:
#* - Make one channel thats a weighted average of all channels
#* - apply frequency extraction (DWT, FFT) 

#* run PPSCOR
