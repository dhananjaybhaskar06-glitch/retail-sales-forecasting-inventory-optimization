import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

df = pd.read_csv("data/raw/sales.csv")
df['Date'] = pd.to_datetime(df['Date'])

results = []
future_all = []

for store in df['Store'].unique():
    for product in df['Product'].unique():
        
        temp = df[(df['Store']==store) & (df['Product']==product)].copy()
        temp = temp.sort_values("Date")
        
        # FEATURES
        temp['day'] = temp['Date'].dt.day
        temp['month'] = temp['Date'].dt.month
        temp['lag_1'] = temp['Sales'].shift(1)
        temp['lag_2'] = temp['Sales'].shift(2)
        temp['rolling_mean'] = temp['Sales'].rolling(3).mean()
        
        temp = temp.dropna()
        
        X = temp[['day','month','lag_1','lag_2','rolling_mean']]
        y = temp['Sales']
        
        model = RandomForestRegressor(n_estimators=100)
        model.fit(X, y)
        
        temp['Predicted'] = model.predict(X)
        
        # FUTURE FORECAST
        future_dates = pd.date_range(temp['Date'].max(), periods=8)[1:]
        
        lag1 = temp.iloc[-1]['Sales']
        lag2 = temp.iloc[-2]['Sales']
        
        for date in future_dates:
            rolling_mean = (lag1 + lag2)/2
            
            row = pd.DataFrame([{
                'day': date.day,
                'month': date.month,
                'lag_1': lag1,
                'lag_2': lag2,
                'rolling_mean': rolling_mean
            }])
            
            pred = model.predict(row)[0]
            
            future_all.append([date, store, product, pred])
            
            lag2 = lag1
            lag1 = pred
        
        # INVENTORY
        lead_time = 5
        std_dev = temp['Sales'].std()
        safety_stock = 1.65 * std_dev * np.sqrt(lead_time)
        
        temp['Reorder_Point'] = temp['Predicted']*lead_time + safety_stock
        
        # STATUS
        temp['Inventory_Status'] = np.where(
            temp['Sales'] < temp['Reorder_Point'], "LOW",
            np.where(temp['Sales'] > temp['Reorder_Point']*1.5, "OVERSTOCK", "OK")
        )
        
        # BUSINESS KPIs
        temp['Revenue'] = temp['Sales'] * temp['Price']
        temp['Profit'] = temp['Revenue'] * 0.2
        
        # ANOMALY DETECTION
        temp['Anomaly'] = np.where(
            abs(temp['Sales'] - temp['rolling_mean']) > 2*temp['Sales'].std(),
            "YES","NO"
        )
        
        results.append(temp)

final_df = pd.concat(results)

future_df = pd.DataFrame(future_all, columns=["Date","Store","Product","Predicted"])

final_df.to_csv("outputs/final_output.csv", index=False)
future_df.to_csv("outputs/future_forecast.csv", index=False)

# PLOT
sample = final_df[(final_df['Store']=="Store_A") & (final_df['Product']=="Milk")]

plt.figure()
plt.plot(sample['Date'], sample['Sales'], label='Actual')
plt.plot(sample['Date'], sample['Predicted'], label='Predicted')
plt.legend()
plt.title("LEVEL MAX Forecast")
plt.savefig("images/level_max.png")
plt.show()

print("LEVEL MAX COMPLETED")