#!/usr/bin/env python
# coding: utf-8

# ## Objective
# The goal of this Data Analysis project using SQL would be to identify opportunities to increase the occupancy rate on low-performing, which can ultimately lead to increased profitability for the airline.

# Database from:
# https://www.kaggle.com/code/prashantverma13/airline-data-analysis-using-sql/input

# # Importing Libraries

# In[1]:


import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')


# # Database Connection

# In[2]:


connection = sqlite3.connect('travel.sqlite')
cursor = connection.cursor()


# In[3]:


cursor.execute("""select name from sqlite_master where type = 'table';""")
print('List of tables present in the database')
table_list = [table[0] for table in cursor.fetchall()]
table_list


# # Data Exploration

# In[4]:


aircrafts_data = pd.read_sql_query("select * from aircrafts_data", connection)
aircrafts_data


# In[5]:


airports_data = pd.read_sql_query("select * from airports_data", connection)
airports_data


# In[6]:


boarding_passes = pd.read_sql_query("select * from boarding_passes", connection)
boarding_passes


# In[7]:


bookings = pd.read_sql_query("select * from bookings", connection)
bookings


# In[8]:


flights = pd.read_sql_query("select * from flights", connection)
flights


# In[9]:


seats = pd.read_sql_query("select * from seats", connection)
seats


# In[10]:


ticket_flights = pd.read_sql_query("select * from ticket_flights", connection)
ticket_flights


# In[11]:


tickets = pd.read_sql_query("select * from tickets", connection)
tickets


# In[12]:


for table in table_list:
    print('\ntable:', table)
    column_info = connection.execute("PRAGMA table_info({})".format(table))
    print(column_info)
    for column in column_info.fetchall():
        print(column[1:3])


# In[13]:


for table in table_list:
    print('\ntable:', table)
    df_table = pd.read_sql_query(f"select * from {table}", connection)
    print(df_table.isnull().sum())


# # Basic Analysis

# **How many planes have more than 100 seats?**

# In[14]:


pd.read_sql_query("""select aircraft_code, count(*) as num_seats 
                        from seats
                        group by aircraft_code
                        having num_seats > 100""", connection)


# **How the number of tickets booked and total amount earned changed with the time?**

# In[15]:


tickets.dtypes


# In[16]:


tickets = pd.read_sql_query("""select * 
                        from tickets
                        inner join bookings
                        on tickets.book_ref = bookings.book_ref""", connection)

tickets['book_date'] = pd.to_datetime(tickets['book_date'])


# In[17]:


tickets['date'] = tickets['book_date'].dt.date
tickets


# In[18]:


x = tickets.groupby('date')[['date']].count()
x.head()


# In[19]:


plt.figure(figsize = (18, 6))
plt.plot(x.index, x['date'], marker = '^')
plt.xlabel('Date', fontsize = 20)
plt.ylabel('Number of Tickets', fontsize = 20)
plt.grid('b')
plt.show()


# In[20]:


bookings = pd.read_sql_query("select * from bookings", connection)
bookings


# In[21]:


bookings['book_date'] = pd.to_datetime(bookings['book_date'])
bookings['date'] = bookings['book_date'].dt.date


# In[22]:


y = bookings.groupby('date')[['total_amount']].sum()
y.head()


# In[23]:


plt.figure(figsize = (18, 6))
plt.plot(y.index, y['total_amount'], marker = '^')
plt.xlabel('Date', fontsize = 20)
plt.ylabel('Total Amount Earned', fontsize = 20)
plt.grid('b')
plt.show()


# **Calculate the average charges for each aircraft with different fare conditions.**

# In[24]:


df = pd.read_sql_query("""select fare_conditions, aircraft_code, avg(amount)
                            from ticket_flights
                            join flights
                            on ticket_flights.flight_id = flights.flight_id
                            group by aircraft_code, fare_conditions""", connection)
df


# In[25]:


sns.barplot(data = df, x = 'aircraft_code', y = 'avg(amount)', hue = 'fare_conditions')


# # Analyzing Occupancy Rate

# **For each aircraft, calculate the total revenue per year and the average revenue per ticket.**

# In[30]:


pd.read_sql_query("""select aircraft_code, ticket_count, total_revenue, total_revenue/ticket_count as avg_revenue_per_ticket
                        from 
                        (select aircraft_code, count(*) as ticket_count, sum(amount) as total_revenue 
                        from ticket_flights
                        join flights
                        on ticket_flights.flight_id = flights.flight_id
                        group by aircraft_code)""", connection)


# **Calculate the average occupancy per aircraft.**

# In[34]:


occupancy_rate = pd.read_sql_query("""select A.aircraft_code, avg(A.seats_count) as booked_seats, B.num_seats, avg(A.seats_count)/B.num_seats as occupancy_rate
                        from 
                        
                        (select aircraft_code, flights.flight_id, count(*) as seats_count
                        from boarding_passes
                        inner join flights
                        on boarding_passes.flight_id = flights.flight_id
                        group by aircraft_code, flights.flight_id) as A
                        
                        inner join
                        
                        (select aircraft_code, count(*) as num_seats
                        from seats
                        group by aircraft_code) as B
                        
                        on A.aircraft_code = B.aircraft_code
                        group by A.aircraft_code""", connection)

occupancy_rate


# **Calculate by how much the total annual turnover could increase by giving all aircraft a 10% higher occupancy rate.**

# In[37]:


occupancy_rate['Inc occupancy rate'] = occupancy_rate['occupancy_rate'] + occupancy_rate['occupancy_rate'] * 0.1
occupancy_rate


# In[40]:


pd.set_option('display.float_format', str)    # To see the number 2.976779e+09 as 2976779410.0


# In[41]:


total_revenue = pd.read_sql_query("""select aircraft_code, sum(amount) as total_revenue
                                       from ticket_flights
                                       join flights 
                                       on ticket_flights.flight_id = flights.flight_id
                                       group by aircraft_code""", connection)

occupancy_rate['Inc Total Annual Turnover'] = (total_revenue['total_revenue'] / occupancy_rate['occupancy_rate']) * occupancy_rate['Inc occupancy rate']
occupancy_rate

