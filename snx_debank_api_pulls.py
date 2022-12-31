# -*- coding: utf-8 -*-
"""
@project: Synthetix Debt Pool Analytics v2.0 via deBank
@author: Darius X1
"""

# import requests
# import pandas as pd
# import json
# import time
import risk_compute_v2 as risk
import snx_debank_api_pulls_functions as fn

C_RATIO = 4
C_RATIO_OP = 4
DUST_USD_AMOUNT = 100

API_KEY = 'f69fc341e57448068077ae48b208908cba32a098'


#%% Get Tokens Prices

ETH, SNX = fn.getTokenPrices()

    
#%% Get top SNX Debt Holders by COLLATERAL

snxTopHolderM, _ = fn.getSNXtopHolders(OE = False, topHoldersCount = 2000)
snxTopHolderO, _ = fn.getSNXtopHolders(OE = True, topHoldersCount = 2000)


#%% Get ADDRESSES of SNX Stakers

addresses = fn.aggregateAddresses(snxTopHolderM, snxTopHolderO, 500)


#%% Get POSITIONS, excluding LPs excluding SNX LP

allPositions, addrPositions = fn.pullSnxPositions(addresses=addresses, dust=DUST_USD_AMOUNT, API_KEY=API_KEY)

                                                 
#%% Get LPs

allLPs, addrLPs = fn.pullSnxLPs(addresses, API_KEY)


#%% HOLDERS, POSITIONS & LPs per ADDRESS

snxTopHolder, addrPosLPs = fn.mergeMnOpPosLPs(snxTopHolderM, snxTopHolderO, addrPositions, addrLPs)


#%% Add Debt Pool Analytics

addrPosLPs = fn.calcDebtPoolAnalytics(addrPosLPs, C_RATIO, C_RATIO_OP, SNX)


# Add:
#   replace USD with sUSD price
#   last claim
#   claim missed
#   deficit or surplus in sUSD to CR


#%% Save tables to Excel

with pd.ExcelWriter('SNX_stakers_tables_lp_positions.xlsx') as writer:  
    addrPosLPs.to_excel(writer, sheet_name='addrPosLPs')
    addrLPs.to_excel(writer, sheet_name='addrLPs', index=True)
    allPositions.to_excel(writer, sheet_name='positions', index=False)
    # allPositions.groupby(['address','chain']).sum().sort_values('valueUSD', ascending=False).round(2).unstack().to_excel(writer, sheet_name='allPositions')
    allLPs.to_excel(writer, sheet_name='LPs', index=False)
    pd.DataFrame(addresses).to_excel(writer, sheet_name='addresses', index=False, header=False)