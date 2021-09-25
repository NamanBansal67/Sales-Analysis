import pandas as pd
import os


# Merge the 12 months of sales data into one csv
files = [file for file in os.listdir('./Sales_Data')]

yearly_data = pd.DataFrame()

for file in files:
    dataframes = pd.read_csv("./Sales_Data/"+file)
    yearly_data = pd.concat([yearly_data, dataframes])

yearly_data.to_csv("concat_data.csv", index=False)


#read concat_data.csv
all_data = pd.read_csv("concat_data.csv")
all_data.head()


#Clean Up Data Values
nan_df = all_data[all_data.isna().any(axis=1)]
all_data = all_data.dropna(how='all')


#find 'Or' and delete
all_data = all_data[all_data['Order Date'].str[0:2] != 'Or']

#convert columns to correct type
all_data['Quantity Ordered'] = pd.to_numeric(all_data['Quantity Ordered']) #to integer
all_data['Price Each'] = pd.to_numeric(all_data['Price Each'])#to float

#Augment Data With Additional Columns
#Adding Month Column
all_data['Month'] = all_data['Order Date'].str[0:2]
all_data['Month'] = all_data['Month'].astype('int32')



#### Determining the best month for sales? How much was earned that month? ####

#Add Sales Column
all_data['Sales'] = all_data['Quantity Ordered'] * all_data['Price Each']


#Add City Column
def get_city(address):
    return address.split(',')[1]

def get_state(address):
    return address.split(',')[2].split(' ')[1]

all_data['City'] = all_data['Purchase Address'].apply(lambda x: get_city(x) + ' ' + get_state(x))


results = all_data.groupby('Month').sum()


#plotting data
import matplotlib.pyplot as plt

months = range(1,13)

plt.bar(months, results['Sales'])
plt.xticks(months)
plt.ylabel('Sales in USD ($)')
plt.xlabel('Month Number')
plt.show()


#determining the city with the highest number of sales

results = all_data.groupby('City').sum()

cities = [city for city, df in all_data.groupby('City')]

plt.bar(cities, results['Sales'])
plt.xticks(cities, rotation='vertical', size=8)
plt.ylabel('Sales in USD ($)')
plt.xlabel('City Number')
plt.show()


#What time should we display advertizements to maximize likelihood of customer's buying products

all_data['Order Date'] = pd.to_datetime(all_data['Order Date'])
all_data['Hour'] = all_data['Order Date'].dt.hour
all_data['Minute'] = all_data['Order Date'].dt.minute

hours = [hour for hour, df in all_data.groupby('Hour')]

plt.plot(hours, all_data.groupby(['Hour']).count())
plt.xticks(hours)
plt.xlabel('Hour')
plt.ylabel('Number of Orders')
plt.grid()
plt.show()




#what products are most often sold together?

df = all_data[all_data['Order ID'].duplicated(keep=False)]
df['Grouped'] = df.groupby('Order ID')['Product'].transform(lambda x:','.join(x))

#getting rid of duplicates
df = df[['Order ID','Grouped']].drop_duplicates()


from itertools import combinations
from collections import Counter

count = Counter()

for row in df['Grouped']:
    row_list = row.split(',')
    count.update(Counter(combinations(row_list, 2)))

for key, value in count.most_common(10):
    print(key, value)


#what products sold the most? why do you think it sold the most?

product_group = all_data.groupby('Product')
quantity_ordered = product_group.sum()['Quantity Ordered']
products = [product for product, df in product_group]
plt. bar(products, quantity_ordered)
plt.ylabel('Quantity Ordered')
plt.xlabel('Product')
plt.xticks(products, rotation='vertical', size=8)
plt.show()


#Overlay with price to make sense of cost
prices = all_data.groupby('Product').mean()['Price Each']

fig, ax1 = plt.subplots()

ax2 = ax1.twinx()
ax1.bar(products, quantity_ordered, color='g')
ax2.plot(products, prices, color='b')

ax1.set_xlabel('Product Name')
ax1.set_ylabel('Quantity Ordered', color='g')
ax2.set_ylabel('Price ($)', color='b')
ax1.set_xticklabels(products, rotation='vertical', size=8)

plt.show()


