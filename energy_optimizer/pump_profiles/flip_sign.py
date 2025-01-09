import pandas as pd

# Load the CSV file
df = pd.read_csv('katwijk_profile.csv')

# Flip the sign of values except for the first row
df.iloc[0:] = df.iloc[0:].apply(lambda x: -x)

# Write the modified DataFrame back to the CSV file
df.to_csv('katwijk_profile_flipped.csv', index=False)