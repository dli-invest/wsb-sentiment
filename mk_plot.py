import seaborn as sns
import pandas as pd
# Apply the default theme
sns.set_theme()

# Load an example dataset
sample = pd.read_csv('sample.csv')
sample.reset_index(drop=True, inplace=True)
sample = sample.loc[:, ~sample.columns.str.contains('^Unnamed')]
wsb_data = sample.drop(columns=['date', 'latest_comment_date', 'domain', 'author'])
# Create a visualization
sns_plot = sns.pairplot(wsb_data, hue='ticker', size=2.5)
sns_plot.savefig("output.png")