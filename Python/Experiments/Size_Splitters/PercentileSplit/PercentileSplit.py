# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 15:00:15 2021

@author: Danie
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
pd.options.mode.chained_assignment = None  # default='warn'

reject_outliers=True # are we not using outliers in this?

# loading the spreadsheet containing all project sizes
df_allRepos = pd.read_excel('../ApacheReposInfo2.xlsx')

#using regex to remove 'k' and 'm' and getting the acutal number
df_allRepos["LOC"] = df_allRepos["LOC"].replace({r'[kK ]': '*1000', r'[mM ]': '*1000000'}, regex=True).map(pd.eval).astype(int) 
df_allRepos["Stars"] = df_allRepos["Stars"].replace({r'[kK ]': '*1000', r'[mM ]': '*1000000'}, regex=True).map(pd.eval).astype(int)
"""
# IF IT STOPS WORKING USE THIS TO FIND WHICH LINE HAS THE BUG (USED THIS TO DISCOVER ERROR IN LINE 482 WHERE THERE WAS AN 'l' CAUSING EVAL NOT TO WORK)
j=0
for i in range(99,len(df_allRepos),1):
    print(j,i)
    print(pd.eval(df_allRepos["LOC"][j:i].map(pd.eval)))
    print()
    
    #df_allRepos["LOC"][j:i] =pd.eval(df_allRepos["LOC"][j:i].map(pd.eval))
    #df_allRepos["Stars"][j:i] =pd.eval(df_allRepos["Stars"][j:i].map(pd.eval))
    
    
    j=i
"""




#sorting in size order
df_allRepos = df_allRepos.sort_values(by=["LOC"]).reset_index()

#outliers are messing with results: getting rid of repos which are much higher than others
if(reject_outliers):
    df_mask=df_allRepos['LOC']<=2000000
    df_allRepos = df_allRepos[df_mask]


#classifying all rows into sizes
df_allRepos["Size_Classification"]=np.NaN

j=0 #start of class (i is end of class)
n=3 #number of splits


#getting the percentile values we need for n splits for the LOC
percentile_step = 1/n
percentiles = [round(this_percentile_step/1000,2) for this_percentile_step in range(int(percentile_step*1000),1000, int(percentile_step*1000))]
print("percentiles", percentiles)
percentiles_values = [df_allRepos["LOC"].quantile(this_percentile_step, "linear") for this_percentile_step in percentiles]
percentiles_values.append(max(df_allRepos["LOC"]))
print("percentiles_values",percentiles_values)

classifier_number = 0 #classification for sizes
#iteratively assign size classifications by checking which percentile each belongs to
for i in range(len(df_allRepos)):
    df_allRepos["Size_Classification"][i]=classifier_number
    if(df_allRepos.iloc[i]["LOC"]>percentiles_values[classifier_number]):
        classifier_number+=1




# Visualisations and useful figures for the different sizes

# Box Plot representing the LOC for different size classifications (generic as we want to experiment with different numbers of classes)
size_classes = np.sort(df_allRepos["Size_Classification"].unique())
data = []
for key in df_allRepos["Size_Classification"].unique():
    data+=[df_allRepos.loc[df_allRepos['Size_Classification'] == key]["LOC"]]

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot(111)
ax.set_title('Boxplot showing LOC distribution between different sized repos')
ax.set_xlabel('Type of Repository')
ax.set_xticklabels(size_classes)
ax.set_ylabel('LOC')
ax.get_yaxis().get_major_formatter().set_scientific(False)
bp = ax.boxplot(data)






# Box Plot showing the distribution of stars
star_data = []
for key in df_allRepos["Size_Classification"].unique():
    star_data+=[df_allRepos.loc[df_allRepos['Size_Classification'] == key]["Stars"]]

fig_4 = plt.figure(figsize=(10,7))
ax_4 = fig_4.add_subplot(111)
ax_4.set_xlabel('Repository size classification')
ax_4.set_xticklabels(size_classes)
ax_4.set_title('Boxplot showing Stars given to diifferent sized repos')
ax_4.set_ylabel('Stars')
star_bp = ax_4.boxplot(star_data)




# Bar Chart representing the distribution of size classifications
distribution_data = []
for key in df_allRepos["Size_Classification"].unique():
    distribution_data+=[len(df_allRepos.loc[df_allRepos['Size_Classification'] == key]["LOC"])]
    


fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot(111)
ax.set_title('Barchart showing distribution between different size classifications')
ax.set_xlabel('Size classification of Repository')
ax.set_ylabel('Number of repositories classified as this')
ax.get_yaxis().get_major_formatter().set_scientific(False)

x_pos = [i for i, _ in enumerate(size_classes)]
bp = ax.bar(x_pos, distribution_data)
plt.xticks(x_pos,size_classes)




#saving all repos with their new size classifications
df_allRepos.to_csv("./PercentileSplit_All.csv", index=False, header=True)

#getting best/worst rated for each size
df_bestRepos = pd.DataFrame(columns=["Name","Repository","Stars","LOC","Size_Classification","Best_or_worst"])

n_best = 10
#n_worst = 10 
gb_allRepos = df_allRepos.groupby("Size_Classification")
for group_name, df_sizeGroup in gb_allRepos:
    df_sizeGroup=df_sizeGroup.sort_values(by="Stars")
    
    #df_nWorst = df_sizeGroup.head(n_worst)
    #df_nWorst["Best_or_worst"]="worst"
    df_nBest = df_sizeGroup.tail(n_best)
    df_nBest["Best_or_worst"]="best"
    
    #df_bestRepos=df_bestRepos.append(df_nWorst)
    df_bestRepos=df_bestRepos.append(df_nBest)

df_bestRepos.to_csv("./PercentileSplit_Best.csv", index=False, header=True)
    

