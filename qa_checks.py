"""qa_checks.py
Implements basic QA checks and writes a simple QA report (JSON).
"""
import pandas as pd
import json
from datetime import timedelta

def missing_value_summary(df):
    return df.isna().sum().to_dict()

def duplicate_orders(df):
    # Check duplicates by merchant, amount, and order_date within 1 minute
    df_sorted = df.sort_values('order_date')
    dup_flags = []
    for i in range(1, len(df_sorted)):
        prev = df_sorted.iloc[i-1]
        cur = df_sorted.iloc[i]
        same_merchant = prev['merchant'] == cur['merchant']
        same_amount = prev['amount_filled'] == cur['amount_filled']
        time_diff = abs((cur['order_date'] - prev['order_date']).total_seconds())
        if same_merchant and same_amount and time_diff <= 60:
            dup_flags.append((prev['order_id'], cur['order_id']))
    return dup_flags

def volume_anomalies_by_merchant(df):
    # Simple day-level counts; flag days with count > mean + 2*std
    df['order_day'] = df['order_date'].dt.date
    grouped = df.groupby(['merchant','order_day']).size().reset_index(name='count')
    anomalies = []
    for merchant, g in grouped.groupby('merchant'):
        mean = g['count'].mean()
        std = g['count'].std(ddof=0)
        threshold = mean + 2*(std if not pd.isna(std) else 0)
        anomalous_days = g[g['count'] > threshold]
        for _, row in anomalous_days.iterrows():
            anomalies.append({'merchant': merchant, 'date': str(row['order_day']), 'count': int(row['count']), 'threshold': float(threshold)})
    return anomalies

def generate_qa_report(df, out_path='qa_report.json'):
    report = {}
    report['missing_values'] = missing_value_summary(df)
    report['duplicates'] = duplicate_orders(df)
    report['volume_anomalies'] = volume_anomalies_by_merchant(df)
    # Basic stats
    report['summary_stats'] = df[['amount_filled']].describe().to_dict()
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2)
    return report

if __name__ == '__main__':
    import sys
    from data_cleaning import run_all_cleaning
    path = sys.argv[1] if len(sys.argv)>1 else 'sample_data.csv'
    df = run_all_cleaning(path)
    report = generate_qa_report(df)
    print('QA report written. Summary:')
    print(report)
