import pandas as pd
import numpy as np

#策略检验模块
class Strategy_verification(object):
    def __init__(self,data):
        data=data.reset_index()
        temp=data['date']
        data.drop(labels=['date'], axis=1,inplace = True)
        data.insert(0,'date', temp)
        #按date列进行重新排序
        data=data.sort_values(by=['date','stk_id'])
        #以date作为一层索引，stk_id作为二层索引重新分表，以便于进行下一步的计算股票持仓比策略操作
        data=data.set_index(['date','stk_id'])
        self.data=data
        data=data.reset_index()
        self.unique_symbol=np.sort(data['stk_id'].unique())
        self.unique_date=np.sort(data['date'].unique())
        
    #回测模块(净值曲线)
    #根据收盘时的数据做分析，但只在开盘操作。且受t+1影响，第一天买的股票只能第二天卖
    #例如，交易信号是在day2收盘时发出的，day3开盘时进行交易，day4开盘时结算利润。以开盘时的收益作为回测曲线
    #总之，以day2收盘价-day1收盘价为主，及其他截至day2收盘时的指标作为自变量，以day4开盘-day3开盘的盈利作为因变量
    #只输出日期和净值，画线需要自行用matplotlib操作
    def backtest(self):
        data=self.data
        unique_date=self.unique_date
        unique_symbol=self.unique_symbol
        backtest_date = unique_date
        total_yield=pd.DataFrame(np.zeros(np.shape(backtest_date)),index=backtest_date,columns=['total_yield'])
        for i in range(len(backtest_date)):
            if i<2:
                total_yield.loc[(backtest_date[i]),'total_yield']=1
            else:
                if np.sum(data.loc[(backtest_date[i-2]),'portfolio_strategy_signal'].values)==0:
                    total_yield.loc[(backtest_date[i]),'total_yield']=total_yield.loc[(backtest_date[i-1]),'total_yield']
                else:
                    data_prepare_1=data.loc[backtest_date[i-2]]
                    data_prepare_2=data.loc[backtest_date[i-1]]
                    data_prepare_3=data.loc[backtest_date[i]]
                    data_prepare_1=data_prepare_1.reset_index()
                    unique_day_symbol=data_prepare_1['stk_id'].values
                    data_prepare_1.set_index(['stk_id'],inplace=True)
                    sum_yield=0
                    for symbol in unique_day_symbol:
                        if data_prepare_1.loc[symbol]['portfolio_strategy_signal']!=0:
                            sum_yield=data_prepare_1.loc[symbol]['portfolio_strategy_signal']*data_prepare_3.loc[symbol]['open']/data_prepare_2.loc[symbol]['open']+sum_yield
                    total_yield.loc[(backtest_date[i]),'total_yield']=total_yield.loc[(backtest_date[i-1]),'total_yield']*sum_yield
        self.total_yield=total_yield
        return total_yield
    
    #基于无风险利率，计算每日超额收益
    def ExcessReturn(self,risk_free_rate):
        total_yield=self.total_yield
        # 计算每日收益率
        total_yield['Return'] = total_yield['total_yield'].pct_change()
        # 计算超额收益
        total_yield['ExcessReturn'] = total_yield['Return'] - ((1+risk_free_rate)**(1/52)-1)
        # 返回结果
        return total_yield['ExcessReturn']
    
    #计算年化收益
    def Annual_Return(self):
        total_yield=self.total_yield
        # 计算年化收益率
        total_return = (total_yield['total_yield'][-1] - total_yield['total_yield'][0]) / total_yield['total_yield'][0]
        annual_return = (1 + total_return) ** (252 / len(total_yield)) - 1  # 假设一年有252个交易日
        return annual_return
    
    #计算年化波动率
    def Annual_Volatility(self):
        total_yield=self.total_yield
        # 计算每日收益率
        total_yield['DailyReturn'] = total_yield['total_yield'].pct_change()
        # 计算年化波动率
        annual_volatility = np.std(total_yield['DailyReturn']) * np.sqrt(252)  # 假设一年有252个交易日
        # 打印结果
        return annual_volatility
    
    #计算夏普比率(以日线为单位)
    def Sharpe_Ratio(self,risk_free_rate):
        total_yield=self.total_yield
        # 计算每日收益率
        total_yield['DailyReturn'] = total_yield['total_yield'].pct_change()
        # 计算平均年化收益率
        average_return = total_yield['DailyReturn'].mean() * 252
        # 计算年化标准差
        volatility = total_yield['DailyReturn'].std() * np.sqrt(252)
        # 计算夏普比率
        sharpe_ratio = (average_return - risk_free_rate) / volatility
        # 返回结果
        return sharpe_ratio
    
    #根据净值曲线，计算最大回撤
    def Max_Drawdown(self):
        total_yield=self.total_yield
        # 计算每日净值相对于最高净值的回撤幅度
        total_yield['Drawdown'] = total_yield['total_yield'] / total_yield['total_yield'].cummax() - 1
        # 计算最大回撤
        max_drawdown = total_yield['Drawdown'].min()
        return max_drawdown
