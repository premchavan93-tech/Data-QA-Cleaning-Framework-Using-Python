"""regex_examples.py
Small examples showing regex usage to extract order numbers, card last4, and keywords from notes.
"""
import re
import pandas as pd

def extract_order_number(note):
    m = re.search(r'order\s*#?(\d+)', note, re.IGNORECASE)
    return m.group(1) if m else None

def extract_card_last4(note):
    m = re.search(r'\*\*\*\*(\d{4})', note)
    return m.group(1) if m else None

def contains_keyword(note, keyword):
    return bool(re.search(re.escape(keyword), note, re.IGNORECASE))

def enrich_df_with_regex(df):
    df['extracted_order_no'] = df['notes'].astype(str).apply(extract_order_number)
    df['card_last4'] = df['notes'].astype(str).apply(extract_card_last4)
    df['promo_flag'] = df['notes'].astype(str).apply(lambda x: contains_keyword(x, 'promo'))
    return df

if __name__ == '__main__':
    df = pd.read_csv((r"C:\Users\Lenovo\Desktop\GitHub\Data QA & Cleaning Framework Using Python\sample_data.csv"), parse_dates=['order_date'])
    df = enrich_df_with_regex(df)
    print(df[['order_id','extracted_order_no','card_last4','promo_flag']])
