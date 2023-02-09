from function import *
from sqlalchemy import create_engine

def sql(empdata,table,databasedb):
    start_time = time.time()
    engine = create_engine("mysql+pymysql://" + userdb + ":" + passworddb + "@" + hostdb + "/" + databasedb)
    empdata.to_sql(table,engine ,index=False,if_exists='replace',method='multi')
   # print("--- %s seconds ---" % (time.time() - start_time))


def Start(path,database):
    df = pd.read_excel(path)
    df['size'] = df.iloc[:, 0].astype(str).str.split('-',expand=True)[1]
    df = df.set_axis(['sku', 'idsell', 'descript', 'unit', 'amount', 'price', 'cost', 'fee', 'etc', 'position','size'], axis=1, inplace=False)
    df.drop(['unit','price','cost','fee','etc','position'],axis='columns',inplace=True)
    sql(df,'stock_vrich',database)

def StartTest(path,database):
    df = pd.read_excel(path)
    df = df.set_axis(['IDorder','a','date', 'FBName', 'cstname', 'addr','b','c', 'tel','d','e', 'trackingNo','f','g', 'total_amount', 'cash', 'discount', 'deli_fee', 'total', 'Ebank', 'paid', 'timepaid', 'thing1', 'thing2', 'idsell', 'descript', 'Comment', 'amount', 'price', 'timedate', 'Printed', 'Checkout', 'Checkout_Time', 'sku'], axis=1, inplace=False)
    df.drop(['a','b','c','d','e','f','g'],axis='columns',inplace=True)
    sql(df,'deli_vrich',database)
    # db.query_commit('insert into muslin.deli_vrich select * from muslin.temp_deli_vrich where Checkout = 1 and idorder not in (select idorder from muslin.deli_vrich)')
# StartTest('stock_20220629180904.xlsx','muslin')
Start('stock_20220629180904.xlsx','muslin')