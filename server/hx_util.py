#!/usr/bin/env python
# encoding=utf8

import json
import requests
import sqlite3

db_path = "./db/hx.db"
config_table = "hx_config"
block_table = "hx_block"
user_table = "hx_user"
asset_table = "hx_asset"

def http_request(method, args):
    url = "http://127.0.0.1:8099"
    args_j = json.dumps(args)
    payload =  "{\r\n \"id\": 1,\r\n \"method\": \"%s\",\r\n \"params\": %s\r\n}" % (method, args_j)
    headers = {
            'content-type': "text/plain",
            'cache-control': "no-cache",
    }
    try:
        response = requests.request("POST", url, data=payload, headers=headers)
        #print type(response)
        #print response.text
        rep = response.json()
        if "result" in rep:
            return rep["result"]
    except Exception:
        return None


def get_asset_info():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('select value from '+config_table+' where key=\'asset_count\'')
    values = cursor.fetchall()
    if len(values) > 0:
        i = int(values[0][0])
    else:
        i = 0
    print("asset count: " + str(i))
    while True:
        asset = http_request('get_asset_imp', ['1.3.'+str(i)])
        if asset is None:
            break
        base_price = float(asset['current_feed']['settlement_price']['base']['amount'])
        quote_price = float(asset['current_feed']['settlement_price']['quote']['amount'])
        if base_price == 0.0 or quote_price == 0.0:
            settlement_price = 0
        else:
            settlement_price = quote_price / base_price * 1000.0
        cursor.execute('insert into '+asset_table+' values (\''+asset['symbol']+'\',\''+asset['id']+'\',\''+str(asset['dynamic_data']['current_supply'])+'\',\''+str(asset['dynamic_data']['withdraw_limition'])+'\',\''+str(settlement_price)+'\')')
        i += 1
    cursor.execute('update '+config_table+' set value=\''+str(i)+'\' where key=\'asset_count\'')
    cursor.close()
    conn.commit()
    conn.close()


def get_account_info():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('select value from '+config_table+' where key=\'account_count\'')
    values = cursor.fetchall()
    i = int(values[0][0])
    print("user count: " + str(i))
    while True:
        if i % 100 == 0:
            print("process 1.2.%d" % i)
        user = http_request('get_account', ['1.2.'+str(i)])
        if user is None:
            break
        cursor.execute('insert into '+user_table+' values (\''+user['name']+'\',\''+user['id']+'\',\''+user['addr']+'\')')
        i += 1
    cursor.execute('update '+config_table+' set value=\''+str(i)+'\' where key=\'account_count\'')
    cursor.close()
    conn.commit()
    conn.close()


def get_account_balances():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('select value from '+config_table+' where key=\'account_count\'')
    values = cursor.fetchall()
    i = int(values[0][0])
    asset_hc = {}
    asset_hx = {}
    asset_ltc = {}
    while True:
        print("process 1.2.%d" % i)
        asset = http_request('get_account_balances', ['1.2.'+str(i)])
        if asset is None:
            break
        else:
            for t in asset:
                if t['asset_id'] == '1.3.3':
                    asset_hc['1.2.'+str(i)] = int(t['amount'])
                elif t['asset_id'] == '1.3.0':
                    asset_hx['1.2.'+str(i)] = int(t['amount'])
                elif t['asset_id'] == '1.3.2':
                    asset_ltc['1.2.'+str(i)] = int(t['amount'])
        i += 1
    cursor.execute('update '+config_table+' set value=\''+str(i)+'\' where key=\'account_count\'')
    cursor.commit()
    conn.close()
    hc_richer = sorted(asset_hc.items(), key=lambda s: s[1], reverse=True)
    hx_richer = sorted(asset_hx.items(), key=lambda s: s[1], reverse=True)
    ltc_richer = sorted(asset_ltc.items(), key=lambda s: s[1], reverse=True)
    print("HC richer:")
    for i in hc_richer:
        if i[1] > 0:
            print(i)
    print("HX richer:")
    for i in hx_richer:
        if i[1] > 0:
            print(i)
    print("LTC richer:")
    for i in ltc_richer:
        if i[1] > 0:
            print(i)


def get_richlist():
    citizens = http_request('list_citizens', [0, 1000])
    asset_hc = {}
    asset_hx = {}
    asset_ltc = {}
    asset_btc = {}
    for c in citizens:
        print("get locked info of " + str(c))
        lockedAssets = http_request('get_citizen_lockbalance_info', [c[0]])
        for a in lockedAssets:
            for item in a[1]:
                if item['amount'] > 0 and item['asset_id'] == '1.3.3':
                    if asset_hc.has_key(a[0]):
                        asset_hc[a[0]] += long(item['amount'])
                    else:
                        asset_hc[a[0]] = long(item['amount'])
                elif item['amount'] > 0 and item['asset_id'] == '1.3.1':
                    if asset_btc.has_key(a[0]):
                        asset_btc[a[0]] += long(item['amount'])
                    else:
                        asset_btc[a[0]] = long(item['amount'])
                elif item['amount'] > 0 and item['asset_id'] == '1.3.0':
                    if asset_hx.has_key(a[0]):
                        asset_hx[a[0]] += long(item['amount'])
                    else:
                        asset_hx[a[0]] = long(item['amount'])
                elif item['amount'] > 0 and item['asset_id'] == '1.3.2':
                    if asset_ltc.has_key(a[0]):
                        asset_ltc[a[0]] += long(item['amount'])
                    else:
                        asset_ltc[a[0]] = long(item['amount'])
        #break
    hc_richer = sorted(asset_hc.items(), key=lambda s: s[1], reverse=True)
    hx_richer = sorted(asset_hx.items(), key=lambda s: s[1], reverse=True)
    ltc_richer = sorted(asset_ltc.items(), key=lambda s: s[1], reverse=True)
    btc_richer = sorted(asset_btc.items(), key=lambda s: s[1], reverse=True)
    print("HC richer:")
    for i in hc_richer:
        if i[1] > 0:
            print("User: %s,\tHC: %d" % (i[0], i[1]/100000000))
    print("HX richer:")
    for i in hx_richer:
        if i[1] > 0:
            print("User: %s,\tHX: %d" % (i[0], i[1]/100000))
    print("LTC richer:")
    for i in ltc_richer:
        if i[1] > 0:
            print(i)
    print("BTC richer:")
    for i in btc_richer:
        if i[1] > 0:
            print(i)


def scan_block(count=1):
    conn = sqlite3.connect('hx.db')
    c = conn.cursor()
    f = open('hx_txs.txt', 'w+')
    for i in range(1, 420332):
        block = http_request('get_block', [i])
        if block is None:
            print("block %d is not fetched" % i)
            continue
        if i % 1000 == 0:
            print("Block height: %d, miner: %s, tx_count: %d" % (block['number'], block['miner'], len(block['transactions'])))
            conn.commit()
            f.flush()
        c.execute("INSERT INTO hx_block VALUES ("+str(block['number'])+",'"+block['miner']+"',"+str(len(block['transactions']))+")")
        if len(block['transactions']) > 0:
            tx_count = 0
            for t in block['transactions']:
                f.write(str(t['operations'])+","+str(block['number'])+","+block['transaction_ids'][tx_count])
                f.write('\n')
            count += 1
            #if count > 10:
                #break

    f.close()
    conn.commit()
    conn.close()


def check_lockinfo(citizen):
    lockedAssets = http_request('get_citizen_lockbalance_info', [citizen])
    for a in lockedAssets:
        user = http_request('get_account', [a[0]])
        hx_amount = 0
        hc_amount = 0
        for s in a[1]:
            if s['asset_id'] == '1.3.0':
                hx_amount = int(s['amount']) / 100000
            if s['asset_id'] == '1.3.3':
                hc_amount = int(s['amount']) / 100000000
        if hc_amount > 0 and hx_amount > 0:
            print(user['name']+": "+hx_amount+", "+hc_amount)

if __name__ == '__main__':
    #scan_block(1)
    #get_richlist()
    check_lockinfo("1.2.738")
