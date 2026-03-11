"""测试备用数据源"""
import sys
sys.path.insert(0, 'src')
from alphalens.backup_data_fetcher import BackupDataFetcher

print('测试备用数据源...')
fetcher = BackupDataFetcher()

print('\n1. 行业列表:')
df = fetcher.get_industry_list()
print(f'   成功: {len(df)} 个行业')
print(f'   示例: {df.iloc[0]["板块名称"]}')

print('\n2. 行业日线:')
df = fetcher.get_industry_daily('半导体')
print(f'   成功: {len(df)} 条数据')

print('\n3. 成分股:')
df = fetcher.get_industry_stocks('半导体')
print(f'   成功: {len(df)} 只股票')

print('\n备用数据源测试完成！')
