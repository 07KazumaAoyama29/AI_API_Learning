## 環境構築
### uvのインストール
```bash
curl -LsSf https://astral.sh/uv/install.sh|sh
```
### uvのパスを通す
#### bash / zshの場合
```bash
source $HOME/.local/bin/env 
```
#### fish の場合
```bash
source $HOME/.local/bin/env.fish 
```
#### 毎回自動でパスを有効化(bash / zsh)
```bash
export PATH="$HOME/.local/bin:$PATH

source ~/.bashrc
```

### 新しいプロジェクトの作成
```bash
uv init test

cd test
```

### Python3.13をinstall
```bash
uv python install 3.13

uv python pin 3.13
```

### 必要なライブラリのインストール
```bash
uv add openai==1.108.1 tiktoken==0.11.0 python-dotenv==1.1.1 requests==2.32.5
```


### APIキーの設定
取得したAPIキーを .env ファイルに書き込む

その後、pythonプログラムを作成し、APIキーが読み込めているかを確認する

```python
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
```

以下のコマンドでpythonファイルを実行できる

```bash
 uv run configure_apyKey.py
```


## API通信を試してみる
### 簡単なチャットを試してみる

```python 
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
                {"role": "user", "content":"こんにちは。1+1の結果をユニークに教えてください。"}
            ]
        )

        print("API接続成功")
        print(f"レスポンス: {response.choices[0].message.content}")
    
    except Exception as e:
        print(f"API接続エラー:{str(e)}")


if __name__ == "__main__":
    main()
```

以下で実行する

```bash
uv run openai_api_test.py
```

## stream出力を試してみる

```python
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
```

