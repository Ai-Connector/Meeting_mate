#!/usr/bin/env python3
"""
API動作確認テストスクリプト
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_api_endpoint(method, endpoint, data=None, expected_status=200):
    """APIエンドポイントをテストする"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        elif method.upper() == "PATCH":
            response = requests.patch(url, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url)
        else:
            print(f"❌ 未対応のメソッド: {method}")
            return False
            
        if response.status_code == expected_status:
            print(f"✅ {method} {endpoint} - Status: {response.status_code}")
            return True
        else:
            print(f"❌ {method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {e}")
        return False

def main():
    print("🚀 API動作確認テスト開始")
    print("=" * 50)
    
    # サーバーの起動確認
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ サーバー起動確認")
        else:
            print("❌ サーバーが起動していません")
            sys.exit(1)
    except:
        print("❌ サーバーに接続できません")
        sys.exit(1)
    
    tests_passed = 0
    tests_total = 0
    
    # 1. 認証エンドポイント
    print("\n📝 認証エンドポイントテスト")
    tests_total += 1
    if test_api_endpoint("POST", "/auth/login", {"email": "test@example.com", "password": "password"}):
        tests_passed += 1
    
    tests_total += 1
    if test_api_endpoint("POST", "/auth/refresh"):
        tests_passed += 1
    
    tests_total += 1
    if test_api_endpoint("GET", "/users/me"):
        tests_passed += 1
    
    # 2. テンプレートエンドポイント
    print("\n📋 テンプレートエンドポイントテスト")
    tests_total += 1
    if test_api_endpoint("GET", "/templates"):
        tests_passed += 1
    
    tests_total += 1
    if test_api_endpoint("GET", "/templates/t1"):
        tests_passed += 1
    
    # 3. 会議エンドポイント
    print("\n🏢 会議エンドポイントテスト")
    tests_total += 1
    if test_api_endpoint("GET", "/meetings"):
        tests_passed += 1
    
    tests_total += 1
    if test_api_endpoint("GET", "/meetings/m1"):
        tests_passed += 1
    
    tests_total += 1
    if test_api_endpoint("GET", "/meetings/m1/full"):
        tests_passed += 1
    
    # 4. 録音エンドポイント
    print("\n🎙️ 録音エンドポイントテスト")
    tests_total += 1
    if test_api_endpoint("GET", "/meetings/m1/recording/status"):
        tests_passed += 1
    
    tests_total += 1
    if test_api_endpoint("POST", "/meetings/m1/recording/start"):
        tests_passed += 1
    
    tests_total += 1
    if test_api_endpoint("POST", "/meetings/m1/recording/stop"):
        tests_passed += 1
    
    # 5. セクションエンドポイント
    print("\n📝 セクションエンドポイントテスト")
    tests_total += 1
    if test_api_endpoint("GET", "/meetings/m1/sections"):
        tests_passed += 1
    
    tests_total += 1
    if test_api_endpoint("GET", "/meetings/m1/sections/status"):
        tests_passed += 1
    
    # 6. 会議アシスト機能エンドポイント
    print("\n🤖 会議アシスト機能エンドポイントテスト")
    tests_total += 1
    if test_api_endpoint("GET", "/meetings/m1/sections/s1/assist"):
        tests_passed += 1
    
    tests_total += 1
    if test_api_endpoint("POST", "/meetings/m1/assist/send", {"assist_type": "general", "custom_message": "テスト"}):
        tests_passed += 1
    
    tests_total += 1
    if test_api_endpoint("POST", "/meetings/m1/assist/reminder", {"section_id": "s1"}):
        tests_passed += 1
    
    # 7. タスクエンドポイント
    print("\n✅ タスクエンドポイントテスト")
    tests_total += 1
    if test_api_endpoint("GET", "/meetings/m1/tasks"):
        tests_passed += 1
    
    # 8. 項目エンドポイント
    print("\n📄 項目エンドポイントテスト")
    tests_total += 1
    if test_api_endpoint("GET", "/meetings/m1/sections/s1/items"):
        tests_passed += 1
    
    # 結果表示
    print("\n" + "=" * 50)
    print(f"📊 テスト結果: {tests_passed}/{tests_total} 成功")
    
    if tests_passed == tests_total:
        print("🎉 すべてのテストが成功しました！")
        return True
    else:
        print(f"⚠️  {tests_total - tests_passed} 個のテストが失敗しました")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)