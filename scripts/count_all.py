import argparse
import requests
import time

def check_api_version(host: str):
    """驗證 API 的標題與版本號"""
    url = f"http://{host}:9846/openapi.json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        title = data.get("info", {}).get("title", "")
        version = data.get("info", {}).get("version", "")
        
        if title != "ibon Data Access API for AI" or version != "1.0312.117":
            print(f"Error: API Validation failed. Title: '{title}', Version: '{version}'")
            print("Expected Title: 'ibon Data Access API for AI'")
            print("Expected Version: '1.0312.117'")
            return False
            
        print("API Validation successful.")
        return True
    except Exception as e:
        print(f"Failed to fetch openapi.json: {e}")
        return False

def count_all_data(host: str):
    """計算資料庫內所有資料筆數，處理 5000 筆上限的分頁"""
    print(f"正在從 http://{host}:9846 開始全量統計資料筆數...")
    
    user_info_url = f"http://{host}:9846/api/v1/ibonUserInfo"
    headers = {"X-API-Key": "siang_20260309"} 
    
    total_count = 0
    skip = 0
    limit = 5000  # 配合 API 單次上限
    
    try:
        start_time = time.time()
        while True:
            params = {"limit": limit, "skip": skip}
            response = requests.get(user_info_url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json().get("data", [])
            batch_size = len(data)
            
            if batch_size == 0:
                break
                
            total_count += batch_size
            skip += limit
            
            if total_count % 25000 == 0:
                elapsed = time.time() - start_time
                print(f"進度：已累計抓取 {total_count} 筆... (耗時: {elapsed:.2f}s)")
                
        end_time = time.time()
        print("\n" + "="*30)
        print("統計完成！")
        print(f"總計資料筆數: {total_count}")
        print(f"總耗時: {end_time - start_time:.2f} 秒")
        print("="*30)
        
    except requests.exceptions.RequestException as e:
        print(f"API 請求錯誤: {e}")
    except Exception as e:
        print(f"執行過程發生錯誤: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ibon Full Data Counter")
    parser.add_argument("--host", type=str, required=True, help="API IP Address, e.g., 127.0.0.1")
    args = parser.parse_args()

    if check_api_version(args.host):
        count_all_data(args.host)
