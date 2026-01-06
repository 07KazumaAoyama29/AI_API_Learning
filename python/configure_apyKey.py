import os
from dotenv import load_dotenv

def main():
    # .envファイル読み込み
    load_dotenv()

    # APIキーが正しく読み込まれているかの確認
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key: print("Open_AI APIキーが正しく設定されています。")
    else: print("Open_AI APIキーが正しく設定されていません。")


if __name__ == "__main__":
    main()
