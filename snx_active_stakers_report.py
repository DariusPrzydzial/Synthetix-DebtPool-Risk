# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 21:09:39 2022

@author: Darius X1
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openpyxl
import time


def load_data():
    
    df_as = pd.read_excel('SNX_stakers_analysis.xlsx',
                       sheet_name='ActiveStakers',
                       index_col=0)
    #df_Mas = pd.read_excel(open('SNX_stakers_analysis.xlsx', 'rb'),
    #                       sheet_name='ActiveStakersAddrMn',
    #                       index_col=0) 
    #df_Oas = pd.read_excel('SNX_stakers_analysis.xlsx',
    #                       sheet_name='ActiveStakersAddrOp',
    #                       index_col=0) 
    df_Msh = pd.read_excel('SNX_stakers_analysis.xlsx',
                           sheet_name='SNXholdersMn',
                           index_col=0) 
    df_Osh = pd.read_excel('SNX_stakers_analysis.xlsx',
                           sheet_name='SNXholdersOp',
                           index_col=0) 
    df_Mds = pd.read_excel('SNX_stakers_analysis.xlsx',
                           sheet_name='DebtSnapshotMn',
                           index_col=0) 
    df_Ods = pd.read_excel('SNX_stakers_analysis.xlsx',
                           sheet_name='DebtSnapshotOp',
                           index_col=0)

    return df_as, df_Msh, df_Osh, df_Mds, df_Ods

def load_data2():
    
    debtPoolAddrPosLPsM = pd.read_excel('SNX_stakers_analysis_lp_positions_MN.xlsx',
                                        sheet_name='debtPoolAddrPosLPsM',
                                        index_col=0)
    debtPoolAddrPosLPsO = pd.read_excel('SNX_stakers_analysis_lp_positions_OP.xlsx',
                                        sheet_name='debtPoolAddrPosLPsO',
                                        index_col=0)

    return debtPoolAddrPosLPsM, debtPoolAddrPosLPsO

def process_data(df_Msh, df_Osh, df_Mds, df_Ods, SNX_PRICE):

    df_Msh.sort_values('collateral', ascending=False, inplace=True)
    df_Msh.reset_index(inplace=True, drop=True)
    df_Mds.sort_values('collateral', ascending=False, inplace=True)
    df_Mds.reset_index(inplace=True, drop=True)
    df_Mds['cRatio'] = (df_Mds.collateral * SNX_PRICE / df_Mds.debtBalanceOf).replace([np.inf, -np.inf], np.nan)#.dropna()
    df_Mds['totalCollateralUSD'] = df_Mds['collateral'] * SNX_PRICE
    df_Mds.rename(columns = {'debtBalanceOf':'debtBalanceOfUSD'}, inplace = True)
    df_Mds['escrowedSNX'] = df_Mds['collateral'] - df_Mds['balanceOf']

    df_Osh.sort_values('collateral', ascending=False, inplace=True)
    df_Osh.reset_index(inplace=True, drop=True)
    df_Ods.sort_values('collateral', ascending=False, inplace=True)
    df_Ods.reset_index(inplace=True, drop=True)
    df_Ods['cRatio'] = (df_Ods.collateral * SNX_PRICE / df_Ods.debtBalanceOf).replace([np.inf, -np.inf], np.nan)#.dropna()
    df_Ods['totalCollateralUSD'] = df_Ods['collateral'] * SNX_PRICE
    df_Ods.rename(columns = {'debtBalanceOf':'debtBalanceOfUSD'}, inplace = True)
    df_Ods['escrowedSNX'] = df_Ods['collateral'] - df_Ods['balanceOf']

    return df_Msh, df_Osh, df_Mds, df_Ods

def mainnet_cratio_snapshot(df_Mds):

    plt.figure(figsize=(15,5))
    plt.subplot(1,2,1)
    df_Mds.sort_values('cRatio').cRatio.head(3000).plot.hist(bins=100, logx=False, logy=False)
    plt.title('Mainnet C-Ratio Histogram, 4 on x axis = 400%')
    plt.subplot(1,2,2)
    df_Mds.sort_values('cRatio').cRatio.head(3000).plot.hist(bins=100, logx=False, logy=True)
    plt.title('Mainnet C-Ratio Histogram, 4 on x axis = 400%, log Y axis')
    plt.show()

def mainnet_cratio_snapshot_low_cratio(df_Mds):

    plt.figure(figsize=(15,5))
    plt.subplot(1,2,1)
    df_Mds.sort_values('cRatio').cRatio.head(2000).plot.hist(bins=100, logx=False, logy=False)
    plt.title('Mainnet C-Ratio Histogram, 4 on x axis = 400%')
    plt.subplot(1,2,2)
    df_Mds.sort_values('cRatio').cRatio.head(2000).plot.hist(bins=100, logx=False, logy=True)
    plt.title('Mainnet C-Ratio Histogram, 4 on x axis = 400%, log Y axis')
    plt.show()

def optimism_cratio_snapshot(df_Ods):

    plt.figure(figsize=(15,5))
    plt.subplot(1,2,1)
    df_Ods.sort_values('cRatio').cRatio.head(12600).plot.hist(bins=100, logx=False, logy=False)
    plt.title('Optimism C-Ratio Histogram, 4 on x axis = 400%')
    plt.subplot(1,2,2)
    df_Ods.sort_values('cRatio').cRatio.head(12600).plot.hist(bins=100, logx=False, logy=True)
    plt.title('Optimism C-Ratio Histogram, 4 on x axis = 400%, log Y axis')
    plt.show()

def optimism_cratio_snapshot_low_cratio(df_Ods):

    plt.figure(figsize=(15,5))
    plt.subplot(1,2,1)
    df_Ods.sort_values('cRatio').cRatio.head(7000).plot.hist(bins=100, logx=False, logy=False)
    plt.title('Mainnet C-Ratio Histogram, 4 on x axis = 400%')
    plt.subplot(1,2,2)
    df_Ods.sort_values('cRatio').cRatio.head(7000).plot.hist(bins=100, logx=False, logy=True)
    plt.title('Mainnet C-Ratio Histogram, 4 on x axis = 400%, log Y axis')
    plt.show()

def mainnet_debt_snapshot_top100(df_Mds):

    df_Mds[['debtBalanceOfUSD','totalCollateralUSD']].head(100).plot(title='Mainnet Debt Snapshot (USD)', figsize=(15,4), style='.-', subplots=False, logy=False);
    df_Mds[['debtBalanceOfUSD','totalCollateralUSD']].head(100).cumsum().plot(title='Mainnet Debt Snapshot Cumulative (USD)', figsize=(15,4), style='.-', subplots=False, logy=False);
    df_Mds[['collateral','balanceOf','escrowedSNX']].head(100).plot(title='Mainnet Debt Snapshot (SNX)', figsize=(15,4), style='.-', subplots=False, logy=False);
    df_Mds[['collateral','balanceOf','escrowedSNX']].head(100).cumsum().plot(title='Mainnet Debt Snapshot Cumulative (SNX)', figsize=(15,4), style='.-', subplots=False, logy=False);


def optimism_debt_snapshot_top100(df_Ods):

    df_Ods[['debtBalanceOfUSD','totalCollateralUSD']].head(100).plot(title='Optimism Debt Snapshot (USD)', figsize=(15,4), style='.-', subplots=False, logy=False);
    df_Ods[['debtBalanceOfUSD','totalCollateralUSD']].head(100).cumsum().plot(title='Optimism Debt Snapshot Cumulative (USD)', figsize=(15,4), style='.-', subplots=False, logy=False);
    df_Ods[['collateral','balanceOf','escrowedSNX']].head(100).plot(title='Optimism Debt Snapshot (SNX)', figsize=(15,4), style='.-', subplots=False, logy=False);
    df_Ods[['collateral','balanceOf','escrowedSNX']].head(100).cumsum().plot(title='Optimism Debt Snapshot Cumulative (SNX)', figsize=(15,4), style='.-', subplots=False, logy=False);

def scattered_charts(df_Mds):
    
    plt.figure(figsize=(15,3));
    fig, axes = plt.subplots(1,3, sharey=False, figsize=(15,4.5));
    df_Mds.plot(ax=axes[0], kind="scatter", x='cRatio', y='collateral', xlim=(.4,100), logx=True, title='C-Ratio vs. CollateralSNX, 4 = 400%');
    df_Mds.plot(ax=axes[1], kind="scatter", x='cRatio', y='debtBalanceOfUSD', xlim=(.4,100), logx=True, title='C-Ratio vs. Debt Balance, 4 = 400%');
    df_Mds.plot(ax=axes[2], kind="scatter", x='totalCollateralUSD', y='debtBalanceOfUSD', logx=False, title='Total Collateral USD vs. Debt Balance USD');

def bubble_charts(df_Mds):
    
    x = df_Mds.cRatio
    y = df_Mds.collateral/1e6
    colors = 'turquoise'#aqua'#mediumseagreen'#aquamarine'
    area = df_Mds.debtBalanceOfUSD/df_Mds.debtBalanceOfUSD.max()*5000
    plt.figure(figsize=(10, 10)) 
    plt.scatter(x, y, s=area, c=colors, alpha=0.3);
    plt.xlim([0, 100]) 
    plt.xlabel('cRatio')
    plt.ylabel('collateralSNX')
    plt.title('C-Ratio vs. CollateralSNX, 4 = 400%')
    plt.show();

    x = df_Mds.cRatio
    y = df_Mds.debtBalanceOfUSD/1e6
    colors = 'turquoise'#aqua'#mediumseagreen'#aquamarine'
    area = df_Mds.debtBalanceOfUSD/df_Mds.debtBalanceOfUSD.max()*5000
    plt.figure(figsize=(10, 10)) 
    plt.scatter(x, y, s=area, c=colors, alpha=0.3);
    plt.xlim([0, 100]) 
    plt.xlabel('cRatio')
    plt.ylabel('debtBalanceOfUSD [M]')
    plt.title('C-Ratio vs. Debt Balance, 4 = 400%')
    plt.show();

    x = df_Mds.totalCollateralUSD/1e6
    y = df_Mds.debtBalanceOfUSD/1e6
    colors = 'turquoise'#aqua'#mediumseagreen'#aquamarine'
    area = df_Mds.debtBalanceOfUSD/df_Mds.debtBalanceOfUSD.max()*5000
    plt.figure(figsize=(10, 10)) 
    plt.scatter(x, y, s=area, c=colors, alpha=0.3);
    plt.xlabel('totalCollateralUSD [M]')
    plt.ylabel('debtBalanceOfUSD [M]')
    plt.title('TotalCollateralUSD vs. DebtBalanceOfUSD')
    plt.show();

def top300_charts(debtPoolAddrPosLPsM, debtPoolAddrPosLPsO):

    M = debtPoolAddrPosLPsM.copy()
    O = debtPoolAddrPosLPsO.copy()
    M[['collateral','debtBalanceOf','posValueUSD','net_usd_value','asset_usd_value','net_usd_value']] = (M[['collateral','debtBalanceOf','posValueUSD','net_usd_value','asset_usd_value','net_usd_value']]/1e6)
    O[['collateral','debtBalanceOf','posValueUSD','net_usd_value','asset_usd_value','net_usd_value']] = (O[['collateral','debtBalanceOf','posValueUSD','net_usd_value','asset_usd_value','net_usd_value']]/1e6)

    plt.figure();
    fig, axes = plt.subplots(1,2, sharex=True, sharey=True, figsize=(15,6));
    M.plot(ax=axes[0], kind="scatter", x='debtBalanceOf', y='collateral', logx=False, title='Mainnet, Total Debt USD [M] vs. Total Collateral SNX [M]');
    O.plot(ax=axes[1], kind="scatter", x='debtBalanceOf', y='collateral', logx=False, title='Optimism, Total Debt USD [M] vs. Total Collateral SNX [M]');
    plt.show();

    plt.figure();
    fig, axes = plt.subplots(1,2, sharex=True, sharey=True, figsize=(15,6));
    M.plot(ax=axes[0], kind="scatter", x='debtBalanceOf', y='claims', logx=False, title='Mainnet, Total Debt USD [M] vs. Claims Count');
    O.plot(ax=axes[1], kind="scatter", x='debtBalanceOf', y='claims', logx=False, title='Optimism, Total Debt USD [M] vs. Claims Count');
    plt.show();

    plt.figure();
    fig, axes = plt.subplots(1,2, sharex=True, sharey=True, figsize=(15,6));
    M.plot(ax=axes[0], kind="scatter", x='debtBalanceOf', y='mints', logx=False, title='Mainnet, Total Debt USD [M] vs. Mints Count');
    O.plot(ax=axes[1], kind="scatter", x='debtBalanceOf', y='mints', logx=False, title='Optimism, Total Debt USD [M] vs. Mints Count');
    plt.show();

    plt.figure();
    fig, axes = plt.subplots(1,2, sharex=True, sharey=True, figsize=(15,6));
    M.plot(ax=axes[0], kind="scatter", x='debtBalanceOf', y='posValueUSD', logx=False, title='Mainnet, Total Debt USD [M] vs. Total Value of All Tokens USD [M]');
    O.plot(ax=axes[1], kind="scatter", x='debtBalanceOf', y='posValueUSD', logx=False, title='Optimism, Total Debt USD [M] vs. Total Value of All Tokens USD [M]');
    plt.show();

    plt.figure();
    fig, axes = plt.subplots(1,2, sharex=True, sharey=True, figsize=(15,6));
    M.plot(ax=axes[0], kind="scatter", x='debtBalanceOf', y='chains', logx=False, title='Mainnet, Total Debt USD [M] vs. Chains with Tokens Count');
    O.plot(ax=axes[1], kind="scatter", x='debtBalanceOf', y='chains', logx=False, title='Optimism, Total Debt USD [M] vs. Chains with Tokens Count');
    plt.show();

    plt.figure();
    fig, axes = plt.subplots(1,2, sharex=True, sharey=True, figsize=(15,6));
    M.plot(ax=axes[0], kind="scatter", x='debtBalanceOf', y='tokens', logx=False, title='Mainnet, Total Debt USD [M] vs. Unique Tokens Count');
    O.plot(ax=axes[1], kind="scatter", x='debtBalanceOf', y='tokens', logx=False, title='Optimism, Total Debt USD [M] vs. Unique Tokens Count');
    plt.show();

    plt.figure();
    fig, axes = plt.subplots(1,2, sharex=True, sharey=True, figsize=(15,6));
    M.plot(ax=axes[0], kind="scatter", x='debtBalanceOf', y='net_usd_value', logx=False, title='Mainnet, Total Debt USD [M] vs. LP Net Value USD [M]');
    O.plot(ax=axes[1], kind="scatter", x='debtBalanceOf', y='net_usd_value', logx=False, title='Optimism, Total Debt USD [M] vs. LP Net Value USD [M]');
    plt.show();

    plt.figure();
    fig, axes = plt.subplots(1,2, sharex=True, sharey=True, figsize=(15,6));
    M.net_usd_value.plot.hist(ax=axes[0], bins=40, alpha=0.5, title='Mainnet, Histogram of LP Net Value USD [M]')
    O.net_usd_value.plot.hist(ax=axes[1], bins=40, alpha=0.5, title='Optimism, Histogram of LP Net Value USD [M]')
    plt.show();

    plt.figure();
    fig, axes = plt.subplots(1,2, sharex=True, sharey=True, figsize=(15,6));
    M.plot(ax=axes[0], kind="scatter", x='debtBalanceOf', y='chains.1', logx=False, title='Mainnet, Total Debt USD [M] vs. LP Chains Count');
    O.plot(ax=axes[1], kind="scatter", x='debtBalanceOf', y='chains.1', logx=False, title='Optimism, Total Debt USD [M] vs. LP Chains Count');
    plt.show();

    plt.figure();
    fig, axes = plt.subplots(1,2, sharex=True, sharey=True, figsize=(15,6));
    M.plot(ax=axes[0], kind="scatter", x='debtBalanceOf', y='pools', logx=False, title='Mainnet, Total Debt USD [M] vs. Unique Pools Count');
    O.plot(ax=axes[1], kind="scatter", x='debtBalanceOf', y='pools', logx=False, title='Optimism, Total Debt USD [M] vs. Unique Pools Count');
    plt.show();

