import pandas as pd
import numpy as np

#持仓比计算模块
class portfolio_strategy_signal(object):
    def __init__(self,data):
        self.data=data
        data=data.reset_index()
        self.unique_symbol=np.sort(data['stk_id'].unique())
        self.unique_date=np.sort(data['date'].unique())
        
    #均仓策略
    def Average_holding(self):
        data=self.data
        data=data.reset_index()
        temp=data['date']
        data.drop(labels=['date'], axis=1,inplace = True)
        data.insert(0,'date', temp)
        #按date列进行重新排序
        data=data.sort_values(by=['date','stk_id'])
        #以date作为一层索引，stk_id作为二层索引重新分表，以便于进行下一步的计算股票持仓比策略操作
        data=data.set_index(['date','stk_id'])
        unique_stock_portfolio=[]
        for date in self.unique_date:
            data_unique_date=data.loc[date]
            if data_unique_date['signal'].sum()==0:
                data_unique_date['unique_stock_portfolio']=data_unique_date['signal']
            else:
                data_unique_date['unique_stock_portfolio']=data_unique_date['signal']/data_unique_date['signal'].sum()
            # 返回交易信号
            unique_stock_portfolio=np.concatenate((unique_stock_portfolio,data_unique_date['unique_stock_portfolio'].values))
        portfolio_strategy_signal=pd.DataFrame(unique_stock_portfolio,columns=['portfolio_strategy_signal'])
        data=data.reset_index()
        data=pd.concat([data,portfolio_strategy_signal],axis=1)
        temp=data['stk_id']
        data.drop(labels=['stk_id'], axis=1,inplace = True)
        data.insert(0,'stk_id', temp)
        #按date列进行重新排序
        data=data.sort_values(by=['stk_id','date'])
        #以date作为一层索引，stk_id作为二层索引重新分表，以便于进行下一步的计算股票持仓比策略操作
        data=data.set_index(['stk_id','date'])
        portfolio_strategy_signal=data['portfolio_strategy_signal']
        self.data=pd.concat([self.data,portfolio_strategy_signal],axis=1)
        return self.data
