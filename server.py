import psycopg2
from parserdb import config
import socket
import json
from urllib.parse import urlparse,parse_qs
from datetime import datetime
from decimal import Decimal

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
        while True:
            conn, addr = server.accept()
            request=conn.recv(1024).decode()
            headers=request.splitlines()[0]
            if headers.startswith('OPTIONS'):#Handle preflight request and cors header issues
                conn.send(preflight_headers.encode('utf-8'))
                continue
            request=process_get_request(headers,conn) if request.startswith('GET') else process_post_request(request,conn) 
            response(conn,request)
    except KeyboardInterrupt as error:
        print(error)
    finally:
        # conn.close()
        server.close()


def process_get_request(headers,conn):#process post request by extracting the request from the http POST method body
    try:
        url=headers.split(" ")[1]
        parse_url=urlparse(url)
        table_name=parse_url.path.replace('/'," ").strip()
        query_param=parse_qs(parse_url.query)
        data={'table_name':table_name,'columns':{k:v[0] for k,v in query_param.items()}}
        match data['table_name']:
            case 'transaction':
                 print('transaction called')
                 db_response=get_users_transation(data['columns'])
            case 'assets':
                db_response=get_all_assets()
            case 'portfolio':
                db_response=get_user_portfolio(data['columns'])
        return db_response
    except Exception as error:
        print(error)
#GET queies
def get_all_assets():
    crs=connect_db()
    columns=['assets_id','assets_name','symbol','type','current_price']
    assets_query="select * from assets"
    crs.execute(assets_query)
    assets=crs.fetchall()
    all_assets=[]
    for asset in assets:
        data=dict((zip(columns,asset)))
        data['current_price']=float(data['current_price'])
        all_assets.append(data)
    db_assets=json.dumps(all_assets)
    print(db_assets)
    return db_assets


def get_user_portfolio(data): #get users portfolio
    try:
        match data:
            case {'user_id':user_id,'asset':asset} if user_id == data['user_id'] and not asset:
                query=f"""
                SELECT assets_name,symbol,type,quantity,(current_price * quantity) AS assets_value,username
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
            case {'user_id':user_id,'asset':asset} if user_id==data['user_id'] and asset==data['asset']:
                    query=f"""
                    SELECT assets_name,symbol,type,quantity,(current_price * quantity) AS assets_value,username
                    FROM portfolio p
                    JOIN assets a ON a.assets_id=p.asset_id
                    JOIN users u ON u.users_id=p.user_id
                    WHERE user_id={data['user_id']} and assets_name='{data['asset']}'
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
                    portfolio={"username":portfolio_data[0][5],"total_portfolio_value":sum(total_asset),"assets":assets}
        
        return json.dumps(portfolio)
    except Exception as e:
        print(e)

def get_users_transation(data):# will refactore this later to handle not just only user transaction but all transaction done in the past in the day
        try:
            match data:
                case {'user_id':user_id} if user_id==data['user_id']:
                    all_transaction=f"""
                    SELECT assets_name,symbol,type,trans_type,trans_quantity,trans_price,trans_time
                    FROM transaction t
                    JOIN assets a on a.assets_id=t.asset_id
                    WHERE user_id={data['user_id']}
                    """
                    crs=connect_db()
                    crs.execute(all_transaction)
                    rsp=crs.fetchall()
                    results=[]
                    column_name=('assets_name','symbol','type','trans_type','trans_quantity','trans_price','trans_time')
                    for x in rsp:
                        result=dict((zip(column_name,x)))
                        result['trans_price']=float(result['trans_price'])
                        result['trans_quantity']=float(result['trans_quantity'])
                        result['trans_time']=result['trans_time'].strftime('%y-%m-%d %H:%m')
                        results.append(result)
                    db_response=json.dumps(results)
                    return db_response
        except (Exception,SyntaxError,ValueError,IndexError) as error:
            print(error)

def process_post_request(request,conn):#extract get request from the url of the http GET method
    if '\r\n\r\n' in request:
        headers,body=request.split('\r\n\r\n',1)
        data=json.loads(body)
        crs=connect_db()
        transaction(conn,data,crs)
        msg={"status":'OK'}
        return json.dumps(msg)

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



handle_connections()
