import psycopg2
from parserdb import config

def connect_db():
    connection=None
    try:
        db_param=config()
        connection=psycopg2.connect(**db_param)
        print(f'{db_param['user']} connected to database')
        connection.autocommit=True
        crs=connection.cursor()
        table="select table_name from information_schema.tables where table_schema='general'"
        select_table='select * from portfolio'
        trans_value={'user_id':3,'asset_id':3,'trans_type':'SELL','trans_quantity':-280,'trans_price':45000,'update':'INSERT'}
        # def function update_portfolio(userID,assetID,trans_type,quantity,price):
            
        def  transaction_func():
            try:
                crs.execute('BEGIN')
                transaction=f"""
                INSERT INTO transaction(user_id,asset_id,trans_type,trans_quantity,trans_price)
                    VALUES({trans_value['user_id']},{trans_value['asset_id']},'{trans_value['trans_type']}',{trans_value['trans_quantity']},{trans_value['trans_price']})
                """
                crs.execute(transaction)
                owned_quantity__query=f"""
                select quantity from portfolio p
                where p.user_id=3 and p.asset_id=3
                """
                crs.execute(owned_quantity__query)
                result=crs.fetchall()
                print(len(result),result)
                owned_quantity=result[0][0] if result else 0
                print(owned_quantity)
                if trans_value['trans_type']=='SELL' and trans_value['trans_quantity'] > owned_quantity and result:
                    raise ValueError('cannot sell more than owned')
                quantity_update=(
                    f"GREATEST({owned_quantity} - {trans_value['trans_quantity']})"
                    if trans_value['trans_type']=='SELL'
                    else f" {owned_quantity} + {trans_value['trans_quantity']}"
                )
                transaction=f"""
                INSERT INTO portfolio(user_id,asset_id,quantity)
                    VALUES({trans_value['user_id']},{trans_value['asset_id']},{trans_value['trans_quantity']})
                    ON CONFLICT(user_id,asset_id)
                    DO UPDATE
                    SET quantity={quantity_update}
                """
                crs.execute(transaction)
                delet_port="delete from portfolio where quantity=0"
                crs.execute(delet_port)
                crs.execute('COMMIT')
            except ValueError as error:
                crs.execute('ROLLBACK')
                print(error)
            finally:
                crs.close()

        transaction_func()
    except (Exception,psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()
            print('database connection terminated')

connect_db()