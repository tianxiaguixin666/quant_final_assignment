import pandas as pd
import numpy as np

#数据处理类
class Data_preprocessing(object):
    def __init__(self,data):
        self.unique_symbol=np.sort(data['stk_id'].unique())
        self.unique_date=pd.to_datetime(np.sort(data['date'].unique()))
        self.data=data.set_index(['stk_id','date'])
        
    #数据插补函数
    def Data_interpolation(self):
        data_fill=pd.DataFrame()
        for symbol in self.unique_symbol:
            #提取单只股票的时间序列
            data_unique_symbol=self.data.loc[symbol]
            # 提取第一个日期
            first_date=data_unique_symbol.index[0]
            mask=(self.unique_date>=first_date)&(self.unique_date<=self.unique_date[-1])
            all_date=self.unique_date[mask]
            trading_days = pd.to_datetime(all_date)
            # 创建一个新的DataFrame，以交易日作为索引，并填充缺失值为NaN
            trading_days={'date':trading_days}
            all_trading_days=pd.DataFrame(trading_days)
            all_trading_days = all_trading_days.set_index(['date'])
            # 将股票日线数据与新的DataFrame合并，根据交易日进行对齐
            merged_data = pd.concat([all_trading_days, data_unique_symbol], axis=1)
            merged_data = merged_data.loc[data_unique_symbol.index[0]:all_trading_days.index[-1]]
            # 使用fillna()函数填充缺失值，将缺失交易日的数据插补为上一个交易日的数据
            data_unique_symbol_filled=merged_data[merged_data.columns].fillna(method='ffill')
            data_unique_symbol_filled.index=pd.MultiIndex.from_product([[symbol], data_unique_symbol_filled.index])
            data_fill=pd.concat([data_fill,data_unique_symbol_filled])
        data_fill=data_fill.reset_index()
        new_column_names={'level_0':'stk_id'}
        data_fill=data_fill.rename(columns=new_column_names)
        data_fill=data_fill.set_index(['stk_id','date'])
        self.data=data_fill.reset_index()
        return data_fill
    
    #数据截取函数
    def Data_intercept(self,stock,start_date='2020-01-02',end_date='2022-12-30'):
        data_intercept=pd.DataFrame()
        for symbol in stock:
            data_unique_symbol=self.data.loc[symbol].reset_index()
            # 使用条件筛选截取指定日期范围的数据
            data_unique_symbol['date'] = pd.to_datetime(data_unique_symbol['date'])
            filtered_data=data_unique_symbol[(data_unique_symbol['date'] >= start_date) & (data_unique_symbol['date'] <= end_date)]
            filtered_data=filtered_data.set_index(['date'])
            filtered_data.index=pd.MultiIndex.from_product([[symbol], filtered_data.index])
            data_intercept=pd.concat([data_intercept,filtered_data])
        data_intercept=data_intercept.reset_index()
        new_column_names={'level_0': 'stk_id'}
        data_intercept=data_intercept.rename(columns=new_column_names)
        data_intercept=data_intercept.set_index(['stk_id','date'])
        self.data=data_intercept
        return data_intercept