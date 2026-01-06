## API呼び出しの基本構文と動作確認
### 基本プログラム

"""python
import os
from openai import OpenAI
from dotenv import load_dotenv

def generate_text(prompt):
    # .envファイル読み込み
    load_dotenv()

    # OpenAIクライアントを初期化
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
    
    try:
        response = client.chat.completions.create(
            model = "gpt-5-nano",
            messages=[
                {"role": "user", "content":prompt}
            ],
            stream=True,
        )
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                print(delta, end="", flush=True)

        print()  # 最後に改行
    except Exception as e:
        print(f"API接続エラー:{str(e)}")
        return None

def main():

    generate_text("格言を一つ教えてください。")

if __name__ == "__main__":
    main()
"""

### systemロールの比較実験
systemロールに技術専門家と初心者向けアシスタントという異なる設定を与え、
同じ質問に対する回答がどう変わるかを比較する