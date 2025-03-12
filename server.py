import psycopg2
from parserdb import config
import socket
import json
from urllib.parse import urlparse,parse_qs
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
            print('connected successfully')
            handle_clients(conn,headers)
    except KeyboardInterrupt as error:
        print(error)
    finally:
        conn.close()
        server.close()


def handle_clients(client_sock,headers):
    try: 
        data=url_parser(headers)
        connect_db(data)
        # print(db_response)
        # id=0
        # msg={'assets_id':'','assets_name':'','symbol':'','type':'','price':''}
        # while id <= len(db_response):
        #     msg.update(dict(zip(msg.keys(),db_response[id])))
        #     msg={k:str(v) if isinstance(v,Decimal) else v for k,v in msg.items()}
        #     id+=1
        #     print(msg)
        # complete_response=cors_header + json.dumps(msg)
        # client_sock.send(complete_response.encode('utf-8'))
        # print('msg delivered successfully')
    except Exception as error:
        print(error)

def url_parser(headers):
    if headers.startswith(('GET','POST')):
        url=headers.split(" ")[1]
        parse_url=urlparse(url)
        table_name=parse_url.path.replace('/'," ").strip()
        query_param=parse_qs(parse_url.query)
        data={'table_name':table_name,'columns':{k:v[0] for k,v in query_param.items()}}
        return data

def connect_db(data):
    try:
        db_params=config()
        connect=psycopg2.connect(**db_params)
        print('data base connected successfully')
        connect.autocommit=True
        crs=connect.cursor()
        transaction(data,crs )
    except psycopg2.DatabaseError as error:
        print(error)
    finally:
        crs.close()


def transaction(data,crs):
    try:
        crs.execute('BEGIN')
        insert=f"""
        INSERT INTO transaction(user_id,asset_id,trans_type,trans_quantity,trans_price)
            VALUES({int(data['columns']['user_id'])},{int(data['columns']['asset_id'])},'{data['columns']['trans_type']}',{int(data['columns']['trans_quantity'])},{int(data['columns']['trans_price'])})
        """
        crs.execute(insert)
        crs.execute('select * from transaction')
        fetch_trans=crs.fetchall()
        print('fetching from transaction')
        print(fetch_trans)
        port_quantity_query=f"""
        SELECT quantity FROM portfolio WHERE user_id={int(data['columns']['user_id'])}
        """
        crs.execute(port_quantity_query)
        quantity_response=crs.fetchall()
        port_quantity= quantity_response[0][0] if quantity_response else 0
        print(port_quantity)
        print(type(data['columns']['trans_quantity']),data['columns']['trans_quantity'])
        if data['columns']['trans_type'] =='SELL' and int(data['columns']['trans_quantity']) > port_quantity and quantity_response:
            raise ValueError('cannnot sell more than owned')
        print('i am here now')
        quantity=(
            port_quantity - int(data['columns']['trans_quantity'])
            if data['columns']['trans_type']=='SELL'
            else port_quantity + int(data['columns']['trans_quantity'])
            )
        print(quantity)
        portfolio=f"""
        INSERT INTO portfolio(user_id,asset_id,quantity)
            VALUES({data['columns']['user_id']},{data['columns']['asset_id']},{data['columns']['trans_quantity']})
            ON CONFLICT(user_id,asset_id)
            DO UPDATE
            SET quantity=GREATEST({quantity},0)
        """
        crs.execute(portfolio)
        crs.execute('select * from portfolio')
        fetch_port=crs.fetchall()
        delete_port='delete from portfolio where quantity=0'
        crs.execute(delete_port)
        print('fetching from portfolio')
        print(fetch_port)
        print('portfolio executed')
        crs.execute('COMMIT')
    except Exception as error:
        print(error)
        crs.execute('ROLLBACK')


def assets():
    asset="select * from assets"
handle_connections()
