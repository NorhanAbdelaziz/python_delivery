import psycopg2
import pandas as pd
import pickle
import numpy as np
import sqlalchemy as db
conn = psycopg2.connect(
   database="ires", user='iti', password='iti', host='localhost', port= '5432'
)
cursor = conn.cursor()

sql ='''CREATE TABLE IF NOT EXISTS irisTable(
  SepalLengthCm decimal,
  SepalWidthCm decimal,
  PetalLengthCm decimal,
  PetalWidthCm decimal,
  prediction VARCHAR(50)
)'''
cursor.execute(sql)
conn.commit()

conn.close()
model = pickle.load(open('model.pkl', 'rb'))
SepalLengthCm = input("Enter the length of Sepal in cm : ")
SepalWidthCm = input("Enter the width of Sepal in cm : ")
PetalLengthCm = input("Enter the length of Petal in cm : ")
PetalWidthCm = input("Enter the width of Petal in cm : ")
# initialize list of lists
data = [[SepalLengthCm, SepalWidthCm, PetalLengthCm, PetalWidthCm]]
  
# Create the pandas DataFrame
df = pd.DataFrame(data, columns = ['sepallengthcm', 'sepalwidthcm', 'petallengthcm', 'petalwidthcm'])
df['prediction'] = model.predict(df)
print(df.head())
con = db.create_engine('postgresql://iti:iti@localhost:5432/ires')
df.to_sql('iristable', con,schema='public', if_exists='append', index=False)
