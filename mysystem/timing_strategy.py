import numpy as np
import pandas as pd

#时序策略类
class timing_strategy(object):
    def __init__(self,data):
        self.data=data
        data=data.reset_index()
        self.unique_symbol=np.sort(data['stk_id'].unique())
        self.unique_date=np.sort(data['date'].unique())
    
    #金叉策略
    def Golden_Cross_Strategy(self):
        data=self.data
        unique_symbol=self.unique_symbol
        unique_date=self.unique_date
        signal=[]
        for symbol in unique_symbol:
            #提取单只股票的时间序列
            data_unique_symbol=data.loc[symbol]
            # 计算均线
            data_unique_symbol['5_day_ma'] = data_unique_symbol['close'].rolling(window=5).mean()
            data_unique_symbol['10_day_ma'] = data_unique_symbol['close'].rolling(window=10).mean()
            # 生成交易信号
            data_unique_symbol['signal'] = np.where(data_unique_symbol['5_day_ma'] > data_unique_symbol['10_day_ma'], 1, 0)
            # 返回交易信号
            signal=np.concatenate((signal,data_unique_symbol['signal'].values))
        signal=pd.DataFrame(signal,columns=['signal'])
        data=data.reset_index()
        data=pd.concat([data,signal],axis=1)
        data=data.set_index(['stk_id','date'])
        self.data=data
        return self.data
