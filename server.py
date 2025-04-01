import psycopg2
from parserdb import config
import socket
import json
from urllib.parse import urlparse,parse_qs
from datetime import datetime
from decimal import Decimal
import requests
import threading
import asyncio
import httpx

server = socket.socket()
port = 1998
server_IP = ''  
server.bind((server_IP, port))
server.listen()
print('Server is listening for connections!!!')

cors_header = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: application/json\r\n"
    "Access-Control-Allow-Origin: *\r\n"
    "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
    "Access-Control-Allow-Headers: Content-Type\r\n"
    "\r\n"  
)
preflight_headers=(
    "HTTP/1.1 204 NO CONTENT\r\n" 
    "Access-Control-Allow-Methods:GET,POST,OPTIONS\r\n"
    "Access-Control-Allow-Headers:Content-Type\r\n"
    "Access-Control-Allow-Origin:*\r\n"
    "Content-Type:applicatin/json\r\n"
)

def handle_connections():
    try:
        crs=connect_db()
        crs.execute('select * from assets')
        initial_assets_fetch=crs.fetchall()
        if not len(initial_assets_fetch) ==0:
            # print('i am here')
            pass
        else:
            print('original fetch')
            assets=fetch_assets()
            # print('i am here')
            for asset in assets:
                # print('asset executed')
                asset_argument=",".join(['%s'] * len(asset['asset_info']['av']))
                query=f"INSERT INTO assets({asset['asset_info']['ac']}) values({asset_argument})"
                crs.execute(query,(asset['asset_info']['av']))
                descr_argument=",".join(['%s'] * len(asset['description']['dv']))
                des=f"INSERT INTO assets_description({asset['description']['dc']}) values({descr_argument})"
                crs.execute(des,(asset['description']['dv']))
                # print('last query executed')
        while True:
            conn, addr = server.accept()
            data=conn.recv(1024).decode()
            if data.startswith('OPTIONS'):#Handle preflight request and cors header issues
                conn.send(preflight_headers.encode('utf-8'))
                continue
            server_response=process_request(conn,data)
            response(conn,server_response)
    except KeyboardInterrupt as error:
        print(error)
    finally:
        server.close()

def process_request(client,request):#process all http request
    try:
        headers,body=request.split('\r\n\r\n',1)
        if headers.startswith('GET'):
            header=headers.splitlines()[0]
            url=header.split(' ')[1]
            parse_url=urlparse(url)
            table_name=parse_url.path.replace('/'," ").strip()
            query_param=parse_qs(parse_url.query)
            data={'table_name':table_name,'columns':{k:v[0] for k,v in query_param.items()}}
            match data['table_name']:
                case 'transaction':
                     db_response=get_users_transation(data['columns'])
                case 'assets':
                    db_response=get_all_assets()
                case 'portfolio':
                    db_response=get_user_portfolio(data['columns'])
            return db_response
        else:
            data=json.loads(body)
            crs=connect_db()
            transaction(client,data,crs)
            msg={"status":'OK'}
        return json.dumps(msg)
            
    except Exception as error:
        print(error)
#GET queies
#100% done with assets endpoint
def get_all_assets():
    crs=connect_db()
    columns=['id','assets_name','symbol','type','price','market_cap','percent_change_24h','logo']
    assets_query="select id,assets_name,symbol,type,price,market_cap,percent_change_24h,logo from assets limit 50"
    crs.execute(assets_query)
    assets=crs.fetchall()
    all_assets=[]
    for asset in assets:
        data=dict((zip(columns,asset)))
        data['price']=float(data['price'])
        data['market_cap']=float(data['market_cap'])
        data['percent_change_24h']=float(data['percent_change_24h'])
        all_assets.append(data)
    db_assets=json.dumps(all_assets)
    return db_assets

#done 100% done with portfolio endpoint
def get_user_portfolio(data): #get users portfolio
    try:
        match data:
            case {'user_id':user_id} if user_id == data['user_id'] and len(data) ==1:
                query=f"""
                SELECT assets_name,symbol,type,quantity,(price * quantity) AS assets_value,username
                FROM portfolio p
                JOIN assets a ON a.assets_id=p.asset_id
                JOIN users u ON u.users_id=p.user_id
                WHERE user_id={data['user_id']}
                """
                crs=connect_db()
                crs.execute(query)
                portfolio_data=crs.fetchall()
                columns_name=('assets_name','symbol','type','quantity','assets_value')
                total_asset=[]
                assets=[]
                for value in portfolio_data:
                    data=dict((zip(columns_name,value)))
                    data['quantity']=float(data['quantity'])
                    data['assets_value']=float(data['assets_value'])
                    total_asset.append(data['assets_value'])
                    assets.append(data)
                portfolio={"username":portfolio_data[0][5],"total_value":sum(total_asset),"assets":assets}
                response=json.dumps(portfolio)
                return(response)
            case {'user_id':user_id,'asset':asset} if user_id==data['user_id'] and asset==data['asset']:
                    query=f"""
                    SELECT assets_name,symbol,type,quantity,(price * quantity) AS assets_value,username
                    FROM portfolio p
                    JOIN assets a ON a.assets_id=p.asset_id
                    JOIN users u ON u.users_id=p.user_id
                    WHERE user_id={data['user_id']} and assets_name='{data['asset']}'
                    """
                    crs=connect_db()
                    crs.execute(query)
                    portfolio_data=crs.fetchall()
                    if len(portfolio_data) <=0:
                        raise ValueError(f"sorry you currently dont have {data['asset']} in your portfolio click buy to own it ")
                    columns_name=('assets_name','symbol','type','quantity','assets_value')
                    total_asset=[]
                    assets=[]
                    for value in portfolio_data:
                        data=dict((zip(columns_name,value)))
                        data['quantity']=float(data['quantity'])
                        data['assets_value']=float(data['assets_value'])
                        total_asset.append(data['assets_value'])
                        assets.append(data)
                    portfolio={"username":portfolio_data[0][5],"total_portfolio_value":sum(total_asset),"assets":assets}
                    response=json.dumps(portfolio)
                    return(response)
    except Exception as e:
        print(e)
    except psycopg2.DatabaseError as error:
        print(error)

def get_users_transation(data):#Done with this for now REFACTOR later
    # will refactore this later to handle not just only user transaction but all transaction done in the past in the day
        try:
            print(data)
            
            if data['user_id'] ==data['user_id'] and len(data) ==1:
                query=f"""
                SELECT assets_name,symbol,type,trans_type,trans_quantity,trans_price,trans_time
                FROM transaction t
                JOIN assets a on a.assets_id=t.asset_id
                WHERE user_id={data['user_id']}
                """
            elif data['user_id']==data['user_id'] and len(data)==2:
                print('work for asset')
                query=f"""
                SELECT assets_name,symbol,type,trans_type,trans_quantity,trans_price,trans_time
                FROM transaction t
                JOIN assets a on a.assets_id=t.asset_id
                WHERE user_id={data['user_id']} and assets_name='{data['asset']}'
                """
            else:
                query=f"""
                SELECT assets_name,symbol,type,trans_type,trans_quantity,trans_price,trans_time
                FROM transaction t
                JOIN assets a on a.assets_id=t.asset_id
                WHERE user_id={data['user_id']} and trans_type='{data['trans_type']}' assets_name='{data['asset']}'
                """
                print('the rest values')
            crs=connect_db()
            crs.execute(query)
            rsp=crs.fetchall()
            print(rsp)
            if len(rsp) <= 0:
                print('error was raised')
                raise ValueError('sorry transaction found')
            results=[]
            column_name=('assets_name','symbol','type','trans_type','trans_quantity','trans_price','trans_time')
            for x in rsp:
                result=dict((zip(column_name,x)))
                result['trans_price']=float(result['trans_price'])
                result['trans_quantity']=float(result['trans_quantity'])
                result['trans_time']=result['trans_time'].strftime('%y-%m-%d %H:%m')
                results.append(result)
            db_response=json.dumps(results)
            print(db_response)
            return db_response
        except (Exception,SyntaxError,ValueError,IndexError) as error:
            print(error)

def process_post_request(request,conn):#extract get request from the url of the http GET method
    if '\r\n\r\n' in request:
        headers,body=request.split('\r\n\r\n',1)
        data=json.loads(body)
        

# def retreive_data_from_db(query_request):
#     if (len(query_request['columns'])) ==0:
#         retrieve_all=f"select * from {query_request['table_name']}"
#         return
    


def connect_db(): # Connect to the data
    try:
        db_params=config()
        connect=psycopg2.connect(**db_params)
        connect.autocommit=True
        crs=connect.cursor()
        # query1="""
        # select * from assets
        # """
        # crs.execute(query1)
        # response1=crs.fetchall()
        # print(response1)
        # query2="select column_name from information_schema.columns where table_name='assets'"
        # crs.execute(query2)
        # response2=crs.fetchall()
        # print(response2)
        return crs
    except psycopg2.DatabaseError as error:
        print(error)
    # finally:
    #     crs.close()
def transaction(client,data,crs): # transaction function update the transaction and portfolio table
    try:
        crs.execute('BEGIN')
        validate_trans_client_data(data)
        validate_trans_db_data(crs,data)
        insert=f"""
        INSERT INTO transaction(user_id,asset_id,trans_type,trans_quantity,trans_price)
            VALUES({data['user_id']},{data['asset_id']},'{data['trans_type']}',{data['trans_quantity']},{data['trans_price']})
        """
        crs.execute(insert)
        port_quantity_query=f"""
        SELECT quantity FROM portfolio WHERE user_id={data['user_id']} and asset_id={data['asset_id']}
        """
        crs.execute(port_quantity_query)
        quantity_response=crs.fetchone()
        print(f"quantity:{quantity_response}")
        port_quantity= quantity_response[0] if quantity_response else 0
        print(port_quantity)
        if data['trans_type'] =='SELL' and int(data['trans_quantity']) > port_quantity and quantity_response:
            raise ValueError('cannnot sell more than owned')
        quantity=(
            max(port_quantity - int(data['trans_quantity']),0)
            if data['trans_type']=='SELL'
            else port_quantity + int(data['trans_quantity'])
            )
        print(port_quantity,int(data['trans_quantity']))
        # print('i am here 4')
        print(quantity)
        portfolio=f"""
        INSERT INTO portfolio(user_id,asset_id,quantity)
            VALUES({data['user_id']},{data['asset_id']},{data['trans_quantity']})
            ON CONFLICT(user_id,asset_id)
            DO UPDATE
            SET quantity={quantity}
        """
        crs.execute(portfolio)
        delete_port='delete from portfolio where quantity=0'
        crs.execute(delete_port)
        crs.execute('COMMIT')
    except ValueError as error:
        # print(error)
        valError={"error":str(error)}
        error_respons=json.dumps(valError)
        response(client,error_respons)
    except psycopg2.DatabaseError as error:
        print(error)
        print("DatabaseError:",error)
        crs.execute('ROLLBACK')




def validate_trans_client_data(data):# validate input sent sent by client before inserting into transaction table
    required_data={"user_id","asset_id","trans_type","trans_quantity","trans_price"}
    missing_data_key=required_data - set(data.keys())
    missing_data_values={}
    for k,v in data.copy().items():
        if data[k]==''.strip():
            missing_data_values.update({k:v})
            raise ValueError(f"missing values:f{missing_data_values}")
    if missing_data_key:
        raise ValueError(f"missing data:{','.join(missing_data_key)}")
    if data["trans_quantity"] < 0 or data["trans_price"] < 0:
        raise ValueError(f"Invalid Numbers:Negative numbers not allowed")
    return ValueError


def validate_trans_db_data(crs,data): # validate data from the transaction table in the db to decide weather to insert new data into the transaction table or not
    check_user_asset_existence=f"""
    select users_id,assets_id 
    from users u,assets a
    where u.users_id={data['user_id']} and a.assets_id={data['asset_id']}
    """
    crs.execute(check_user_asset_existence)
    check=crs.fetchall()
    if not check:
        raise ValueError('user or selected assets does not exist')
    

    fetch_duplicate=f"""
    select user_id,asset_id,trans_type,trans_quantity,trans_price,trans_time
    from transaction 
    where user_id={data['user_id']} and CAST(trans_time AS timestamp) > NOW()- INTERVAL '5 seconds'
    """
    crs.execute(fetch_duplicate)
    result=crs.fetchall()
    if result:
        duplicates=result
    else:
        return
    for v in duplicates:
        duplist=list(v)
        last_time=duplist[5]
        del duplist[5]
        dupdata=duplist
        now=datetime.now()
        time_diff=(now-last_time).total_seconds()
    for k,v in data.items():
        if v in dupdata and time_diff < 5:
            raise ValueError('duplicate transaction wait 5s before trying again')
        else:
            return
        
    
def response(client,rsp):# Response route
    rsp=cors_header + rsp
    client.send(rsp.encode('utf-8'))
    client.shutdown(socket.SHUT_RDWR)


def fetch_assets():
    try:
        asset_url='https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        id_url='https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'
        asset_params={"start":"501","limit":"500","convert":"USD"}
        headers={"X-CMC_PRO_API_KEY":"15d50cf2-5669-4a88-92c9-b612e72d415b",
                "Accept":"application/json",
                "Accept-Encoding":"deflate,gzip"}
        response=requests.get(asset_url,headers=headers,params=asset_params)
        if response.status_code==200:
            responses=response.json()
            datas=responses['data']
            # print(datas)
        assets=[]
        asset_ids=[]
        for data in datas:
            asset_iden=str(data['id'])
            asset={asset_iden:{'asset_info':{'assets_id':data['id'],'assets_name':data['name'],'symbol':data['symbol'],'type':'crytpo','price':data['quote']['USD']['price'],'market_cap':data['quote']['USD']['market_cap'],'percent_change_24h':data['quote']['USD']['percent_change_24h']},
            'description':{'asset_description_id':data['id'],'description':'','circulating_supply':data['circulating_supply'],'total_supply':data['total_supply'],'category':'','max_supply':data['max_supply'],'volume_24h':data['quote']['USD']['volume_24h'],'volume_change_24h':data['quote']['USD']['volume_change_24h'], 'percent_change_1h':data['quote']['USD'][ 'percent_change_1h'],'percent_change_24h':data['quote']['USD']['percent_change_24h'],'percent_change_7d':data['quote']['USD']['percent_change_7d'],'percent_change_30d':data['quote']['USD']['percent_change_30d'],'percent_change_60d':data['quote']['USD']['percent_change_60d'],'percent_change_90d':data['quote']['USD']['percent_change_90d'], 'market_cap_dominance':data['quote']['USD'][ 'market_cap_dominance'],'fully_diluted_market_cap':data['quote']['USD']['fully_diluted_market_cap'], 'last_updated':datetime.strptime(data['quote']['USD'][ 'last_updated'],'%Y-%m-%dT%H:%M:%S.%fZ'),'link':''}
            }}
            assets.append(asset)
            asset_ids.append(str(data['id']))
        param={"id":",".join(asset_ids)}
        asset_id_info=requests.get(id_url,headers=headers,params=param)
        if asset_id_info.status_code==200:
            id_data=asset_id_info.json()
            ids=id_data['data']
            real_assets=[]
            for id in ids:
                for asset in assets:
                    if id in asset:
                        asset[id]['asset_info']['logo']=ids[id]['logo']
                        asset[id]['description']['description']=ids[id]['description']
                        asset[id]['description']['category']=ids[id]['category']
                        asset[id]['description']['link']= ids[id]['urls']['website'][0] if  ids[id]['urls']['website'] else " "
                        ac=",".join(asset[id]['asset_info'].keys())
                        av=tuple(asset[id]['asset_info'].values())
                        dc=",".join(asset[id]['description'].keys())
                        dv=tuple(asset[id]['description'].values())
                        asset={'asset_info':{'ac':ac,'av':av},'description':{'dc':dc,'dv':dv}}
                        real_assets.append(asset)
        # print('asset returned')
        return real_assets
    except Exception as error:
        print(error)
        # print(real_assets)
        
# def update_assets():
#     crs=connect_db()
#     assets=fetch_assets()
#     query=f"""
#     updat assets
#     set price=%s,percent_change_24h=%s
#     where symbol=%s
#     """
#     for asset in assets:
#         symbol=asset['symbol']
#         price=asset['price']
#         percent=asset['percent_change_24h']
#     crs.execute(query,(price,percent,symbol))

# threading.Timer(300,update_assets).start()

handle_connections()
