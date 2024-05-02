# -*- coding: utf-8 -*-#
from urllib.parse import urlencode
import pandas as pd
import requests


def gen_secid(rawcode: str) -> str:
    '''
    生成东方财富专用的secid

    Parameters
    ----------
    rawcode : 6 位股票代码

    Return
    ------
    str: 指定格式的字符串

    '''
    # 沪市指数
    if rawcode[:3] == '000':
        return f'1.{rawcode}'
    # 深证指数
    if rawcode[:3] == '399':
        return f'0.{rawcode}'
    # 沪市股票
    if rawcode[0] != '6':
        return f'0.{rawcode}'
    # 深市股票
    return f'1.{rawcode}'


def get_k_history(code: str, beg: str, end: str, klt: int = 101, fqt: int = 1) -> pd.DataFrame:
    '''
    功能获取k线数据
    -
    参数

        code : 6 位股票代码
        beg: 开始日期 例如 20230101
        end: 结束日期 例如 20230201

        klt: k线间距 默认为 101 即日k
            klt:1 1 分钟
            klt:5 5 分钟
            klt:101 日
            klt:102 周
        fqt: 复权方式
            不复权 : 0
            前复权 : 1
            后复权 : 2
    '''
    EastmoneyKlines = {
        'f51': '日期',
        'f52': '开盘',
        'f53': '收盘',
        'f54': '最高',
        'f55': '最低',
        'f56': '成交量',
        'f57': '成交额',
        'f58': '振幅',
        'f59': '涨跌幅',
        'f60': '涨跌额',
        'f61': '换手率',

    }
    EastmoneyHeaders = {

        'User-Agent': 'Mozilla/5.0 (Macintosh; Apple M1 Mac OS X 10_16_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Referer': 'http://quote.eastmoney.com/center/gridlist.html#hs_a_board',
    }
    fields = list(EastmoneyKlines.keys())
    columns = list(EastmoneyKlines.values())
    fields2 = ",".join(fields)
    secid = gen_secid(code)
    params = (
        ('fields1', 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13'),
        ('fields2', fields2),
        ('beg', beg),
        ('end', end),
        ('rtntype', '6'),
        ('secid', secid),
        ('klt', f'{klt}'),
        ('fqt', f'{fqt}'),
    )
    params = dict(params)
    base_url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get'
    url = base_url + '?' + urlencode(params)
    json_response: dict = requests.get(
        url, headers=EastmoneyHeaders).json()

    data = json_response.get('data')
    if data is None:
        if secid[0] == '0':
            secid = f'1.{code}'
        else:
            secid = f'0.{code}'
        params['secid'] = secid
        url = base_url + '?' + urlencode(params)
        json_response: dict = requests.get(
            url, headers=EastmoneyHeaders).json()
        data = json_response.get('data')
    if data is None:
        print('股票代码:', code, '可能有误')
        return pd.DataFrame(columns=columns)

    klines = data['klines']

    rows = []
    for _kline in klines:
        kline = _kline.split(',')
        rows.append(kline)

    df = pd.DataFrame(rows, columns=columns)

    return df


if __name__ == "__main__":
    # 股票代码
    code = '000001'

    # 开始日期
    start_date = '20230101'
    # 结束日期
    end_date = '20231101'

    print(f'正在获取 {code} 从 {start_date} 到 {end_date} 的 k线数据......')
    # 根据股票代码、开始日期、结束日期获取指定股票代码指定日期区间的k线数据
    df = get_k_history(code, start_date, end_date)
    # 保存k线数据到表格里面
    df.to_excel('output.xlsx',index=False)
    print(f'股票代码：{code} 的 k线数据已保存到代码目录下的 {code}.xlsx 文件中')

