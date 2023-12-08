import pandas as pd
import numpy as np

#多股选股策略类
class stock_selection_strategy(object):
    def __init__(self,data):
        self.data=data
        data=data.reset_index()
        self.unique_symbol=np.sort(data['stk_id'].unique())
        self.unique_date=np.sort(data['date'].unique())
        
    #n日反转策略
    def n_days_reversal_strategy(self,n):
        data=self.data
        n_days_up=[]
        for symbol in self.unique_symbol:
            data_unique_symbol=data.loc[symbol]
            data_unique_symbol['n_days_up'] = (data_unique_symbol['close']-data_unique_symbol['close'].shift(n))/data_unique_symbol['close'].shift(n)
            n_days_up=np.concatenate((n_days_up,data_unique_symbol['n_days_up'].values))
        n_days_up=pd.DataFrame(n_days_up,columns=['n_days_up'])
        data=data.reset_index()
        data=pd.concat([data,n_days_up],axis=1)
        #将date和symbol两列交换，按照date的字符串进行升序排列，然后以date作为一层索引，symbol作为二层索引重新分类
        temp=data['date']
        data.drop(labels=['date'], axis=1,inplace = True)
        data.insert(0,'date', temp)
        #按date列进行重新排序
        data=data.sort_values(by=['date','stk_id'])
        #以date作为一层索引，symbol作为二层索引重新分表，以便于进行下一步的计算股票持仓比策略操作
        data=data.set_index(['date','stk_id'])
        signal=[]
        for date in self.unique_date:
            data_unique_date=data.loc[date]
            data_unique_date['rank'] = data_unique_date['n_days_up'].rank(ascending=True)
            data_unique_date['signal'] = np.where((data_unique_date['rank'] < 10) , 1, 0)
            signal=np.concatenate((signal,data_unique_date['signal'].values))
        signal=pd.DataFrame(signal,columns=['signal'])
        data=data.reset_index()
        data=pd.concat([data,signal],axis=1)
        temp=data['stk_id']
        data.drop(labels=['stk_id'], axis=1,inplace = True)
        data.insert(0,'stk_id', temp)
        #按date列进行重新排序
        data=data.sort_values(by=['stk_id','date'])
        #以date作为一层索引，symbol作为二层索引重新分表，以便于进行下一步的计算股票持仓比策略操作
        data=data.set_index(['stk_id','date'])
        self.data=data
        return self.data