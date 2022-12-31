# -*- coding: utf-8 -*-
"""
@project: Synthetix Debt Pool Analytics v2.0 via deBank
@author: Darius X1
"""

import requests
import pandas as pd
import json
import time
import risk_compute_v2 as risk



#%% Get Tokens Prices

def getTokenPrices():
    _c, _all = risk.download_prices(['ETH','SNX','sUSD'], False, False); 
    ETH = _c.tail(1).ETH[0]
    SNX = _c.tail(1).SNX[0]
    print(ETH, SNX)
    return (ETH, SNX)


#%% theGraoh Pull


snxOEmainSubgraphURL = 'https://api.thegraph.com/subgraphs/name/synthetixio-team/optimism-main'
snxMainnetSubgraphURL = 'https://api.thegraph.com/subgraphs/name/synthetixio-team/mainnet-main'

def q_SNXtopHolders(first, last_collateral):
    queryStr = """
    {
        snxholders(first: %s, where: {collateral_lt: "%s"}, orderBy: collateral, orderDirection: desc ) {
            id
            block
            timestamp
            balanceOf
            collateral
            transferable
            initialDebtOwnership
            debtEntryAtIndex
            claims
            mints
        }
    }""" % (first, last_collateral)
    return queryStr


def getSNXtopHolders(OE = True, topHoldersCount = 2000):

    data = []
    pageSize = 1000
    last_collateral = 10**18
    count = 0
    while(count < topHoldersCount):
        query = q_SNXtopHolders(pageSize, last_collateral)
        if OE:
            r = requests.post(snxOEmainSubgraphURL, json={'query': query})
        else:
            r = requests.post(snxMainnetSubgraphURL, json={'query': query})
        page = json.loads(r.text)['data']['snxholders']
        data.extend(page)
        count += len(page)
        print(page[0]['id'], count)
        if len(page) < pageSize:
            break
        last_collateral = page[-1]['collateral']
    if OE:
        print('Pulled details on top ' + str(count) + ' active SNX holders on Optimism' )
    else:
        print('Pulled details on top ' + str(count) + ' active SNX holders on Mainnet' )
    sh = pd.DataFrame(data)
    sh[['balanceOf', 'collateral','transferable']] = sh[['balanceOf', 'collateral','transferable']].fillna(0).astype(float)
    sh[['block', 'claims', 'mints', 'timestamp']] = sh[['block', 'claims', 'mints', 'timestamp']].fillna(0).astype('int64')
    # sh[['id']] = sh[['id']].fillna(0).astype('str')
    sh = sh[['id','collateral','balanceOf','transferable','mints','claims','timestamp']]#.set_index('id')
    sh['chain'] = 'O' if OE else 'M'
    sh[['collateral','balanceOf']].plot(logy=True)
    print('Last updated:', time.ctime(sh.timestamp.max()))

    return sh, count


#%% Functions

def aggregateAddresses(snxTopHolderM, snxTopHolderO, topHold):

    addresses2 = pd.concat([snxTopHolderM.head(topHold), snxTopHolderO.head(topHold)]).reset_index(drop=True)
    addresses2[['collateral','balanceOf']].plot(logy=True)
    addresses = []
    for i in addresses2.id:
        if i not in addresses:
            addresses.append(i)
    len(addresses)
    pd.DataFrame(addresses).to_csv('_addresses.csv', index=False)
    print("Addresses Counts: MainNet", topHold, " Optimism", topHold, " Combined", len(addresses))
    return addresses


def getChains(useApi, API_KEY):
    
    if useApi:
        headers = {
            'accept': 'application/json',
            'AccessKey': API_KEY,
        }
        response = requests.get('https://pro-openapi.debank.com/v1/chain/list', headers=headers)
        response = requests.get(url, headers=headers)
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        table_data = json.loads(content)
        pd.DataFrame(table_data).head(1).T
        chains = pd.DataFrame(table_data)[['name','id']]
        chains.to_csv('snx_deBank_chains.csv', index=False)
    else:
        chains = pd.read_csv('snx_deBank_chains.csv')
    chains_snx = ['eth','matic','op','arb','ftm','xdai','bsc','avax'] # 'celo'
    chains_snx = ['eth','op']
    chains = chains[chains.id.isin(chains_snx)]

    return(chains)


def pullSnxPositions(addresses, dust, API_KEY):

    addressCounter = 0
    apiCallsCount = len(addresses)
    allPositions = pd.DataFrame()
    addrPositions = pd.DataFrame()
    for address in addresses:
        # for chain in chains.id:
            addressCounter += 1
            print([int(addressCounter/apiCallsCount*100),address])
            df = callDebankApi(address, API_KEY)
            allPositions = pd.concat([allPositions, df], sort=False) 
            if not df.empty:
                tmp = allPositions[allPositions.address == address]
                df3 = tmp[['address','valueUSD','chain']].groupby(['address','chain']).sum().sort_values('valueUSD', ascending=False).round(0)
                valueUSD = df3.valueUSD.sum()
                df3 = df3.unstack()
                df3 = df3['valueUSD'].reset_index()
                df3.columns = (['address'] + ['valueUSD-' + n for n in list(df3.columns[1:].values)] )
                df3.set_index('address')
                df3['valueUSD'] = valueUSD
                df3['chains'] = tmp.chain.nunique()
                df3['tokens'] = tmp.chain.count()
                addrPositions = pd.concat([addrPositions, df3], sort=False)

    addrPositions['valueUSD-M-O'] = addrPositions['valueUSD'] - addrPositions['valueUSD-eth'] - addrPositions['valueUSD-op']
    addrPositions = addrPositions.groupby(['address']).sum().sort_values('valueUSD', ascending=False).round(0)
    allPositions.to_csv('_allPositions.csv', index=False)
    addrPositions.reset_index().to_csv('_addrPositions.csv', index=False)
    
    # chart
    allPositions[allPositions.address == allPositions.address.iloc[-1]].pivot_table(index='chain', 
                             columns='symbol',
                             values='valueUSD', 
                             aggfunc='sum').plot.bar(stacked =True, rot=0, figsize=(10,5),
                                                     title=allPositions.address.iloc[-1])

    return (allPositions, addrPositions)


def pullSnxLPs(addresses, API_KEY):

    addressCounter = 0
    apiCallsCount = len(addresses)
    allLPs = pd.DataFrame()
    addrLPs = pd.DataFrame()
    for address in addresses:
        addressCounter += 1
        print([int(addressCounter/apiCallsCount*100),address])
        df = callDebankApi2(address, API_KEY)
        if ~df.name.isna()[0]:
            allLPs = pd.concat([allLPs, df], sort=False) 
            tmp = allLPs[allLPs.address == address]
            df2 = tmp.groupby(['address']).sum().sort_values('net_usd_value', ascending=False).round(2)
            df2['LPchains'] = tmp.chain.nunique()
            df2['LPpools'] = tmp.chain.count()
            if sum(tmp[tmp.name == 'Synthetix'].chain.isin(['eth'])) > 0:
                df2['snx_net_usd'] = tmp.groupby(by=['name','chain'])['net_usd_value'].sum()['Synthetix']['eth']
                df2['snx_asset_usd'] = tmp.groupby(by=['name','chain'])['asset_usd_value'].sum()['Synthetix']['eth']
                df2['snx_debt_usd'] = tmp.groupby(by=['name','chain'])['debt_usd_value'].sum()['Synthetix']['eth']
            else:
                df2['snx_net_usd'] = 0
                df2['snx_asset_usd'] = 0
                df2['snx_debt_usd'] = 0
            if sum(tmp[tmp.name == 'Synthetix'].chain.isin(['op'])) > 0:
                df2['snx_op_net_usd'] = tmp.groupby(by=['name','chain'])['net_usd_value'].sum()['Synthetix']['op']
                df2['snx_op_asset_usd'] = tmp.groupby(by=['name','chain'])['asset_usd_value'].sum()['Synthetix']['op']
                df2['snx_op_debt_usd'] = tmp.groupby(by=['name','chain'])['debt_usd_value'].sum()['Synthetix']['op']
            else:
                df2['snx_op_net_usd'] = 0
                df2['snx_op_asset_usd'] = 0
                df2['snx_op_debt_usd'] = 0
            # df2['snx_asset_usd_value'] = tmp.groupby(by=['name'])['asset_usd_value'].sum()['Synthetix']
            # df2['snx_debt_usd_value'] = tmp.groupby(by=['name'])['debt_usd_value'].sum()['Synthetix']
            df2['other_net_usd'] = df2['net_usd_value'] - df2['snx_net_usd'] - df2['snx_op_net_usd'] 
            df2['other_asset_usd'] = df2['asset_usd_value'] - df2['snx_asset_usd'] - df2['snx_op_asset_usd']
            df2['other_debt_usd'] = df2['debt_usd_value'] - df2['snx_debt_usd'] - df2['snx_op_debt_usd']
            addrLPs = pd.concat([addrLPs, df2], sort=False)
    allLPs.to_csv('_allLPs.csv', index=False)
    addrLPs.reset_index().to_csv('_addrLPs.csv', index=False)
    # chart
    allLPs[allLPs.address == allLPs.address.iloc[3]].pivot_table(index=['chain'], 
                       columns='name',
                       values='net_usd_value', 
                       aggfunc='sum').plot.bar(stacked =True, rot=0, figsize=(10,5),
                                               title=allLPs.address.iloc[3])
    # len(allLPs.address.unique())

    return allLPs, addrLPs


def mergeMnOpPosLPs(snxTopHolderM, snxTopHolderO, addrPositions, addrLPs):
    
    _snxTopHolderO = snxTopHolderO.copy()
    _snxTopHolderO.columns = ['id'] + [i + "O" for i in ['collateral', 'balanceOf', 'transferable', 'mints', 'claims','timestamp']] + ['chain']
    snxTopHolder = pd.concat([snxTopHolderM.set_index('id').drop(['chain'], axis=1), 
                            _snxTopHolderO.set_index('id').drop(['chain'], axis=1)], axis=1).sort_values('collateral', ascending=False).fillna(0)
    addrPosLPs = pd.concat([addrPositions.sort_index(), addrLPs.sort_index()], axis=1)
    addrPosLPs = pd.concat([snxTopHolder, addrPosLPs], axis=1)
    addrPosLPs = addrPosLPs[addrPosLPs.index.isin(addrPositions.index)]
    # addrPosLPs[addrPosLPs.index == '0x99f4176ee457afedffcb1839c7ab7a030a5e4a92']
    addrPosLPs.reset_index().to_csv('_addrPosLPs.csv', index=False)

    return snxTopHolder, addrPosLPs 


#%% Add Debt Pool Analytics

def calcDebtPoolAnalytics(addrPosLPs, C_RATIO, C_RATIO_OP, SNX):

    addrPosLPs['snxTotalDebt'] = addrPosLPs.snx_debt_usd + addrPosLPs.snx_op_debt_usd
    addrPosLPs.sort_values('snxTotalDebt', ascending=False, inplace=True)

    addrPosLPs['asset-50pct'] = addrPosLPs.snx_asset_usd * 0.5
    addrPosLPs['asset-40pct'] = addrPosLPs.snx_asset_usd * 0.6
    addrPosLPs['asset-30pct'] = addrPosLPs.snx_asset_usd * 0.7
    addrPosLPs['asset-20pct'] = addrPosLPs.snx_asset_usd * 0.8
    addrPosLPs['asset-10pct'] = addrPosLPs.snx_asset_usd * 0.9
    addrPosLPs['asset+10pct'] = addrPosLPs.snx_asset_usd * 1.1
    addrPosLPs['asset+20pct'] = addrPosLPs.snx_asset_usd * 1.2
    addrPosLPs['asset+30pct'] = addrPosLPs.snx_asset_usd * 1.3
    addrPosLPs['asset+40pct'] = addrPosLPs.snx_asset_usd * 1.4
    addrPosLPs['asset+50pct'] = addrPosLPs.snx_asset_usd * 1.5
    
    addrPosLPs['asset_op-50pct'] = addrPosLPs.snx_op_asset_usd * 0.5
    addrPosLPs['asset_op-40pct'] = addrPosLPs.snx_op_asset_usd * 0.6
    addrPosLPs['asset_op-30pct'] = addrPosLPs.snx_op_asset_usd * 0.7
    addrPosLPs['asset_op-20pct'] = addrPosLPs.snx_op_asset_usd * 0.8
    addrPosLPs['asset_op-10pct'] = addrPosLPs.snx_op_asset_usd * 0.9
    addrPosLPs['asset_op+10pct'] = addrPosLPs.snx_op_asset_usd * 1.1
    addrPosLPs['asset_op+20pct'] = addrPosLPs.snx_op_asset_usd * 1.2
    addrPosLPs['asset_op+30pct'] = addrPosLPs.snx_op_asset_usd * 1.3
    addrPosLPs['asset_op+40pct'] = addrPosLPs.snx_op_asset_usd * 1.4
    addrPosLPs['asset_op+50pct'] = addrPosLPs.snx_op_asset_usd * 1.5
    
    addrPosLPs['cRatio'] = addrPosLPs.snx_asset_usd / addrPosLPs.snx_debt_usd
    addrPosLPs['cRatioOP'] = addrPosLPs.snx_op_asset_usd / addrPosLPs.snx_op_debt_usd
    addrPosLPs['snxPrice'] = SNX
    addrPosLPs['snxPricePct2cRatio'] = C_RATIO / addrPosLPs['cRatio'] - 1
    addrPosLPs['snxPricePct2cRatioOP'] = C_RATIO_OP / addrPosLPs['cRatioOP'] - 1
    addrPosLPs['snxPrice2cRatioOP'] = (addrPosLPs['snxPricePct2cRatioOP'] + 1) * SNX
    addrPosLPs['debtBurnMint2cRatio'] = (- addrPosLPs.snx_debt_usd * (4 - addrPosLPs['cRatio']) / C_RATIO)
    addrPosLPs['debtBurnMint2cRatioOP'] = (- addrPosLPs.snx_op_debt_usd * (4 - addrPosLPs['cRatioOP']) / C_RATIO_OP)

    addrPosLPs['sUSD_cr+100bps'] = addrPosLPs.snx_asset_usd/(C_RATIO + 1.0) - addrPosLPs.snx_debt_usd 
    addrPosLPs['sUSD_cr+50bps']  = addrPosLPs.snx_asset_usd/(C_RATIO + 0.5) - addrPosLPs.snx_debt_usd 
    addrPosLPs['sUSD_cr+0bps']   = addrPosLPs.snx_asset_usd/(C_RATIO + 0.0) - addrPosLPs.snx_debt_usd 
    addrPosLPs['sUSD_cr-50bps']  = addrPosLPs.snx_asset_usd/(C_RATIO - 0.5) - addrPosLPs.snx_debt_usd 
    addrPosLPs['sUSD_cr-100bps'] = addrPosLPs.snx_asset_usd/(C_RATIO - 1.0) - addrPosLPs.snx_debt_usd 
    addrPosLPs['sUSD_cr+100bps_SNX-20pct'] = addrPosLPs.snx_asset_usd * 0.8 / (C_RATIO + 1.0) - addrPosLPs.snx_debt_usd 
    addrPosLPs['sUSD_cr+50bps_SNX-20pct']  = addrPosLPs.snx_asset_usd * 0.8 / (C_RATIO + 0.5) - addrPosLPs.snx_debt_usd 
    addrPosLPs['sUSD_cr+0bps_SNX-20pct']   = addrPosLPs.snx_asset_usd * 0.8 / (C_RATIO + 0.0) - addrPosLPs.snx_debt_usd 
    addrPosLPs['sUSD_cr-50bps_SNX-20pct']  = addrPosLPs.snx_asset_usd * 0.8 / (C_RATIO - 0.5) - addrPosLPs.snx_debt_usd 
    addrPosLPs['sUSD_cr-100bps_SNX-20pct'] = addrPosLPs.snx_asset_usd * 0.8 / (C_RATIO - 1.0) - addrPosLPs.snx_debt_usd 
    
    addrPosLPs['sUSD_cr_op+100bps'] = addrPosLPs.snx_op_asset_usd/(C_RATIO_OP + 1.0) - addrPosLPs.snx_op_debt_usd 
    addrPosLPs['sUSD_cr_op+50bps']  = addrPosLPs.snx_op_asset_usd/(C_RATIO_OP + 0.5) - addrPosLPs.snx_op_debt_usd 
    addrPosLPs['sUSD_cr_op+0bps']   = addrPosLPs.snx_op_asset_usd/(C_RATIO_OP + 0.0) - addrPosLPs.snx_op_debt_usd 
    addrPosLPs['sUSD_cr_op-50bps']  = addrPosLPs.snx_op_asset_usd/(C_RATIO_OP - 0.5) - addrPosLPs.snx_op_debt_usd 
    addrPosLPs['sUSD_cr_op-100bps'] = addrPosLPs.snx_op_asset_usd/(C_RATIO_OP - 1.0) - addrPosLPs.snx_op_debt_usd 
    addrPosLPs['sUSD_cr_op+100bps_SNX-20pct'] = addrPosLPs.snx_op_asset_usd * 0.8 / (C_RATIO_OP + 1.0) - addrPosLPs.snx_op_debt_usd 
    addrPosLPs['sUSD_cr_op+50bps_SNX-20pct']  = addrPosLPs.snx_op_asset_usd * 0.8 / (C_RATIO_OP + 0.5) - addrPosLPs.snx_op_debt_usd 
    addrPosLPs['sUSD_cr_op+0bps_SNX-20pct']   = addrPosLPs.snx_op_asset_usd * 0.8 / (C_RATIO_OP + 0.0) - addrPosLPs.snx_op_debt_usd 
    addrPosLPs['sUSD_cr_op-50bps_SNX-20pct']  = addrPosLPs.snx_op_asset_usd * 0.8 / (C_RATIO_OP - 0.5) - addrPosLPs.snx_op_debt_usd 
    addrPosLPs['sUSD_cr_op-100bps_SNX-20pct'] = addrPosLPs.snx_op_asset_usd * 0.8 / (C_RATIO_OP - 1.0) - addrPosLPs.snx_op_debt_usd 
    
    return addrPosLPs


def callDebankApi(address, API_KEY):
    import requests
    headers = {
        'accept': 'application/json',
        'AccessKey': API_KEY,
    }
    params = {
        'id': address,
        'is_all': 'false',
    }
    response = requests.get('https://pro-openapi.debank.com/v1/user/all_token_list', params=params, headers=headers)
    if response.status_code == 200 and response.text != '[]\n':
        content = response.content
        # soup = BeautifulSoup(content, 'html.parser')
        table_data = json.loads(content)
        df = pd.DataFrame(table_data)
        if not df.empty:
            df['valueUSD'] = df.amount * df.price
            df[['chain','optimized_symbol','symbol','amount','price','valueUSD','is_core']].sort_values('valueUSD', ascending=False)
            df = df[['chain','optimized_symbol','symbol','amount','price','valueUSD','is_core']].sort_values('valueUSD', ascending=False)
        # else:
        #     df = pd.DataFrame(index = [0], columns = ['chain','optimized_symbol','symbol','amount','price','valueUSD','is_core'])
        #     # df.chain = chain

        # df.insert(loc=0, column='name', value=name)
        df.insert(loc=0, column='address', value=address)
        df.sort_values('valueUSD', ascending=False, inplace=True)
    else:
        df = pd.DataFrame(index = [0], columns = ['chain','optimized_symbol','symbol','amount','price','valueUSD','is_core'])
        df = pd.DataFrame()

    return(df)


def callDebankApi2(address, API_KEY):

    # https://docs.open.debank.com/en/reference/api-pro-reference/user#get-user-simple-protocol-list-on-all-supported-chains
    import requests
    headers = {
        'accept': 'application/json',
        'AccessKey': API_KEY,
    }
    params = {
        'id': address,
    }
    response = requests.get('https://pro-openapi.debank.com/v1/user/all_simple_protocol_list', params=params, headers=headers)

    # url = f"https://openapi.debank.com/v1/user/simple_protocol_list?id={address}&chain_id={chain}"
    # response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.content
        # soup = BeautifulSoup(content, 'html.parser')
        table_data = json.loads(content)
        df = pd.DataFrame(table_data)
        if not df.empty:
            df = df[['chain','id','name','net_usd_value','asset_usd_value','debt_usd_value']].sort_values('net_usd_value', ascending=False)
        else:
            df = pd.DataFrame(index = [0], columns = ['chain','id','name','net_usd_value','asset_usd_value','debt_usd_value'])
    else:
        df = pd.DataFrame(index = [0], columns = ['chain','id','name','net_usd_value','asset_usd_value','debt_usd_value'])
    df.insert(loc=0, column='address', value=address)
    df.sort_values('net_usd_value', ascending=False, inplace=True)

    return(df)