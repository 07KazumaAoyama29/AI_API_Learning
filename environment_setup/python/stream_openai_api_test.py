import os
from openai import OpenAI
from dotenv import load_dotenv

def main():
    # .envファイル読み込み
    load_dotenv()

    # OpenAIクライアントを初期化
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

    try:
        #シンプルなテスト用プロンプト
        response = client.chat.completions.create(
            model = "gpt-5-nano",
            messages=[
                {"role": "user", "content":"プログラミングにおける、環境構築って英語でなんて言うの？"}
            ],
            stream=True,
        )

        print("API接続成功")
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                print(delta, end="", flush=True)

        print()  # 最後に改行
    
    except Exception as e:
        print(f"API接続エラー:{str(e)}")


if __name__ == "__main__":
    main()
