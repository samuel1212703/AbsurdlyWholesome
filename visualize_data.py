import matplotlib.pyplot as plt
import pandas as pd

print("###### Data Visualization ######")

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

headers = ['Date', 'Link-Karma', 'Comment-Karma']

df = pd.read_csv('karma.csv', names=headers)

df.set_index('Date').plot()

plt.show()
