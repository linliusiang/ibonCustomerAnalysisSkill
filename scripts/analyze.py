import argparse
import requests
import pandas as pd

def check_api_version(host: str):
    """驗證 API 的標題與版本號"""
    url = f"http://{host}:9846/openapi.json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        title = data.get("info", {}).get("title", "")
        version = data.get("info", {}).get("version", "")
        
        if title != "ibon Data Access API for AI" or version != "1.0312.115":
            print(f"Error: API Validation failed. Title: '{title}', Version: '{version}'")
            print("Expected Title: 'ibon Data Access API for AI'")
            print("Expected Version: '1.0312.115'")
            return False
            
        print("API Validation successful.")
        return True
    except Exception as e:
        print(f"Failed to fetch openapi.json: {e}")
        return False

def analyze_data(host: str):
    """提取資料並進行基本分析"""
    print(f"Fetching data from http://{host}:9846 ...")
    
    store_url = f"http://{host}:9846/api/v1/StoreDesc"
    user_info_url = f"http://{host}:9846/api/v1/ibonUserInfo"

    try:
        # NOTE: 由於 API 要求 X-API-Key，這裡暫時給一個預設值，若有真實 key 請替換
        headers = {"X-API-Key": "siang_20260309"} 
        
        # 由於門市很多，利用 skip 與 limit 分頁抓取所有門市
        stores = []
        skip = 0
        limit = 10000
        while True:
            store_params = {"limit": limit, "skip": skip}
            store_res = requests.get(store_url, headers=headers, params=store_params)
            store_res.raise_for_status()
            batch = store_res.json().get("data", [])
            if not batch:
                break
            stores.extend(batch)
            skip += limit
            
        # 針對 UserInfo，目前抓 202603，抓 10000 筆
        user_params = {
            "limit": 10000, 
            "LogTime_start": "20260301000000",
            "LogTime_end": "20260331235959"
        }
        user_res = requests.get(user_info_url, headers=headers, params=user_params)
        user_res.raise_for_status()
        users = user_res.json().get("data", [])

        df_stores = pd.DataFrame(stores)
        df_users = pd.DataFrame(users)

        print(f"取得門市資訊筆數: {len(df_stores)}")
        print(f"取得 2026 年 3 月的交易客群紀錄筆數: {len(df_users)}")

        if not df_stores.empty and not df_users.empty:
            df_users['StoreID'] = df_users['StoreID'].astype(str).str.strip()
            df_stores['Store_id'] = df_stores['Store_id'].astype(str).str.strip()
            
            # 依據 StoreID 和 Store_id 進行合併
            df_merged = pd.merge(df_users, df_stores, left_on='StoreID', right_on='Store_id', how='left')
            
            if 'Address' in df_merged.columns:
                df_merged['Address'] = df_merged['Address'].fillna('')
                df_target = df_merged[df_merged['Address'].str.contains('內湖', na=False)]
                
                if df_target.empty:
                    print("找不到內湖區的資料，但列出有找到的有效地址資料：")
                    df_merged = df_merged[df_merged['Address'] != '']
                else:
                    df_merged = df_target
                
                print(f"最終篩選出的資料筆數: {len(df_merged)}")

            if df_merged.empty:
                print("篩選後無符合條件的資料可供分析。")
                return

            # 客群分析 (年齡與性別)
            if 'Gender' in df_merged.columns and 'AGE' in df_merged.columns:
                print("\n--- 篩選地區：性別與年齡分佈 ---")
                dist = df_merged.groupby(['Gender', 'AGE']).size().reset_index(name='Count')
                print(dist.to_string(index=False))

            # 情緒分析
            if 'Emotions' in df_merged.columns:
                print("\n--- 情緒分佈 ---")
                print(df_merged['Emotions'].value_counts().to_string())

            # 操作按鈕分析
            if 'LevelName_2' in df_merged.columns:
                print("\n--- 首頁按鈕使用次數 ---")
                print(df_merged['LevelName_2'].value_counts().head(10).to_string())

        else:
            print("無足夠資料進行分析。")
            
    except requests.exceptions.RequestException as e:
        print(f"API 請求錯誤: {e}")
    except Exception as e:
        print(f"分析過程發生錯誤: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ibon Customer Analysis")
    parser.add_argument("--host", type=str, required=True, help="API IP Address, e.g., 127.0.0.1")
    args = parser.parse_args()

    # 驗證通過後才執行分析
    if check_api_version(args.host):
        analyze_data(args.host)
