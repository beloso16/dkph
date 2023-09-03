"""
Using R/Python, you are asked to discover other points of the business by investigating
the following:
1. Produce a report of the top 5 models per month in physical stores. How much
sales did they generate and what is its contribution (proportion in %) to overall
sales?
2. What is the ratio of identified transactions (transactions made by members) per
store? Rank them from highest to lowest.
3. Find the average basket value and average basket size per store. Which stores
are performing well? Which ones are not? Please state your consideration(s).
4. If there is any timing of the day that is most popular """

import pandas as pd

#get the file
txns_df = pd.read_csv ('~/Desktop/recruitment_transactions_201907_201912.csv', low_memory=False)
print("all txns")
#print(txns_df)

#remove duplicates if any
txns_df.drop_duplicates(subset=None, keep='first', inplace=False, ignore_index=False)

#assuming txns with 0 qty did not push through
txns_df = txns_df[txns_df['f_qty_item'] != 0]

print(txns_df)

#get only in-store txns
offline_txns_df = txns_df[txns_df['the_to_type'] == 'offline']

#get total sales
total_sales = txns_df['f_to_tax_in'].sum()
print("total sales")
print(total_sales)


##### 1 TOP 5 MODELS
#get sum by model
sum_by_model = offline_txns_df.groupby(['mdl_num_model_r3'])['f_to_tax_in'].sum().reset_index()
print("sum by model")
print(sum_by_model)

#get top 5 models
top_5_models = offline_txns_df.groupby(['mdl_num_model_r3'])['f_to_tax_in'].sum().reset_index().sort_values(by='f_to_tax_in', ascending=[False]).head(n=5)

#get % contribution per model
top_5_models['perc_contribution'] = top_5_models['f_to_tax_in']*100/total_sales
print("top 5 models")
print(top_5_models)
#export to csv
top_5_models.to_csv("~/Desktop/dkph.csv", mode='a', header=True)

##### 2 MEMBER TRANSACTION RATIO
#made by members only
members_only = offline_txns_df[offline_txns_df['ctm_customer_id'].notna()]
#group by business unit
members_only = members_only.groupby(['but_name_business_unit'])['the_transaction_id'].nunique().reset_index(name='member_txns')

#made by non-members only
non_members_only = offline_txns_df[offline_txns_df['ctm_customer_id'].isna()]
#group by business unit
non_members_only = non_members_only.groupby(['but_name_business_unit'])['the_transaction_id'].nunique().reset_index(name='non_member_txns')

#merge the two dataframes
all_txns = pd.merge(members_only, non_members_only, on='but_name_business_unit', how='right')
#ratio of member txns
all_txns['member_transaction_ratio'] = all_txns['member_txns'] / (all_txns['member_txns'] + all_txns['non_member_txns'])
all_txns = all_txns[['but_name_business_unit', 'member_transaction_ratio']].sort_values(by='member_transaction_ratio', ascending=[False])
print("member txn ratio")
print(all_txns)
all_txns.to_csv("~/Desktop/dkph.csv", mode='a', header=True)

#####3 AVERAGE BASKET SIZE PER STORE
# no of txns per store
no_of_transactions = offline_txns_df.groupby(['but_name_business_unit'])['the_transaction_id'].count().reset_index(name='no_of_transactions')

# gmv per store
total_gmv = offline_txns_df.groupby(['but_name_business_unit'])['f_to_tax_in'].sum().reset_index(name='total_basket_value')

# merge no of txns and gmv
offline_txns_df = pd.merge(offline_txns_df, no_of_transactions, on='but_name_business_unit')
offline_txns_df = pd.merge(offline_txns_df, total_gmv, on='but_name_business_unit')

# average basket value = gmv / no of txns
offline_txns_df['average_basket_value'] = offline_txns_df['total_basket_value'] / offline_txns_df['no_of_transactions']

# total qty per store
total_qty = offline_txns_df.groupby(['but_name_business_unit'])['f_qty_item'].sum().reset_index(name='total_qty')

# add total qty to df
offline_txns_df = pd.merge(offline_txns_df, total_qty, on='but_name_business_unit')

# average basket size = total qty / no of txns
offline_txns_df['average_basket_size'] = offline_txns_df['total_qty'] / offline_txns_df['no_of_transactions']

# group by store
averages = offline_txns_df.groupby(['but_name_business_unit'])[['average_basket_value', 'average_basket_size']].mean()

print("average basket value and basket size")
print(averages)
averages.to_csv("~/Desktop/dkph.csv", mode='a', header=True)

#####4 MOST POPULAR TIME OF DAY
txns_df['timestamp'] = pd.to_datetime(txns_df['the_date_transaction'])
# get hr of day
txns_df['hour_of_day'] = txns_df['timestamp'].dt.hour
popular_time = txns_df.groupby(['hour_of_day'])['the_transaction_id'].count().reset_index(name='no_of_txns').sort_values(by='no_of_txns', ascending=[False]).head(n=5)
print("popular time")
print(popular_time)
popular_time.to_csv("~/Desktop/dkph.csv", mode='a', header=True)
