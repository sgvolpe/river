import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = {'x': np.arange(100), 'y': np.arange(100)}
df = pd.DataFrame(data)

for each in [df.head(10), df.info(), df.describe(), df.groupby(by=['x']).sum(), df.unstack(level=0),
             df.fillna(0), df.join(df, df, rsuffix='r_'), pd.merge([df, df])
             ]:
    print(each)



df['x'].plot()

plt.show()
