## API呼び出しの基本構文と動作確認
### 基本プログラム

Open AI APIを使用するときは、公式が提供するライブラリを使うことで、効率的かつ安全委APIを呼び出すことができる。

まずは、公式ライブラリを使った、シンプルなテキスト生成を行うプログラムを作成する。

environmental_setupで作成したプログラムとほぼ同じ。関数化をして安全性を高めているだけ。

```python
import os, sys, time
from openai import OpenAI
from dotenv import load_dotenv

def generate_text(prompt):
    # .envファイル読み込み
    load_dotenv()

    # OpenAIクライアントを初期化
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

    t0 = time.perf_counter()
    first_token_time = None
    
    try:
        stream = client.responses.create(
        model="gpt-5-nano",
        input=prompt,
        stream=True,

        #推論を最小化
        reasoning={"effort": "minimal"},  
        )

        buf = []
        last_flush = time.perf_counter()
        FLUSH_INTERVAL = 0.03  # 30msごとにまとめて表示

        for event in stream:
            if event.type == "response.output_text.delta":
                if first_token_time is None:
                    first_token_time = time.perf_counter()
                    print(f"TTFT: {(first_token_time - t0)*1000:.0f} ms\n---")
                buf.append(event.delta)

                now = time.perf_counter()
                if now - last_flush >= FLUSH_INTERVAL:
                    sys.stdout.write("".join(buf))
                    sys.stdout.flush()
                    buf.clear()
                    last_flush = now

            elif event.type == "response.output_text.done":
                if buf:
                    sys.stdout.write("".join(buf))
                    sys.stdout.flush()
                print()
    except Exception as e:
        print(f"API接続エラー:{str(e)}")
        return None

def main():

    generate_text("格言を一つ教えてください。")

if __name__ == "__main__":
    main()


```

ここで重要なポイントは以下の３つ。

- APIキーの管理:
環境変数(プログラムが実行される環境において、外部から設定される変数)から安全に API キーを取得することで、安全に認証情報を管理できる。

ここでいう環境変数とは

```python
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
```

のこと。

- message パラメータ:
会話形式の入力を辞書形式で指定する。AIの振る舞いを柔軟に制御できる。

- 例外処理:
try, exceptの例外処理を書くことで、ネットワークエラーやレート制限などの問題に自動で対処できるようになる。

### systemロールの比較実験
systemロールに技術専門家と初心者向けアシスタントという異なる設定を与え、
同じ質問に対する回答がどう変わるかを比較する。

```python
import os, sys, time
from openai import OpenAI
from dotenv import load_dotenv

def chat_with_system_role(system_content, user_content):
    # .envファイル読み込み
    load_dotenv()

    # OpenAIクライアントを初期化
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

    t0 = time.perf_counter()
    first_token_time = None
    
    try:
        stream = client.responses.create(
        model="gpt-5-nano",
        input=user_content,
        instructions=system_content,
        stream=True,

        #推論を最小化
        reasoning={"effort": "minimal"},  
        )

        buf = []
        last_flush = time.perf_counter()
        FLUSH_INTERVAL = 0.03  # 30msごとにまとめて表示

        for event in stream:
            if event.type == "response.output_text.delta":
                if first_token_time is None:
                    first_token_time = time.perf_counter()
                    print(f"TTFT: {(first_token_time - t0)*1000:.0f} ms\n---")
                buf.append(event.delta)

                now = time.perf_counter()
                if now - last_flush >= FLUSH_INTERVAL:
                    sys.stdout.write("".join(buf))
                    sys.stdout.flush()
                    buf.clear()
                    last_flush = now

            elif event.type == "response.output_text.done":
                if buf:
                    sys.stdout.write("".join(buf))
                    sys.stdout.flush()
                print()
    except Exception as e:
        print(f"API接続エラー:{str(e)}")
        return None

def main():
    user_content = "動物のゾウとはどのようなものですか？"

    print("幼稚園児ver")
    system_content = "あなたは幼稚園児です。"
    chat_with_system_role(system_content, user_content)

    print("-"*50)

    print("専門家ver")
    system_content = "あなたは生物研究の専門家です。"
    chat_with_system_role(system_content, user_content)

if __name__ == "__main__":
    main()

```

同じ質問でも、ロールによって応答の詳しさや語調がかなり変わる。


### 出力制御パラメータについて

API には、 AI の応答品質を左右する、重要なパラメータが複数用意されている。

プロンプトの工夫(プロンプトエンジニアリング)だけではなく、これらのパラメータを調整することで
より精度・品質の高い出力を得られることができる。

#### GPT-5-nanoで指定可能なパラメータ

以下は model: "gpt-5-nano" で client.responses.create(...) に渡せる
(= Responses APIのCreateで受け付けられる)リクエストボディのトップレベル引数の全一覧[[1]](https://platform.openai.com/docs/api-reference/)

```txt
model, input, instructions, previous_response_id, conversation, prompt, text, reasoning（※gpt-5系のみ）, tools, tool_choice, parallel_tool_calls
max_tool_calls, max_output_tokens, truncation, stream, stream_options, include, background, store, metadata, service_tier, safety_identifier
prompt_cache_key, prompt_cache_retention, user（Deprecated。prompt_cache_key / safety_identifier へ移行推奨）
```

#### ①temperature(創造性の制御)

temperature は出力の安定性と多様性のバランスを調整するパラメータ。

低い場合は安定した答え、高い場合は表現に幅が出やすくなる(実行するごとに出力が変わる)。

AI の API のパラメータの中で、一番有名なのではないか。

しかし、GPT-5-nano では temperature は設定不可になっている。

OpenAIのモデルガイド(3036-01-27アクセス)では、

temperature / top_p / logprobs は「GPT-5.2 で reasoning.effort: "none" のときだけ」サポート

それ以外の reasoning effort（none以外）や、古い GPT-5 系（gpt-5, gpt-5-mini, gpt-5-nano）にこれらを含めるとエラーになる

と明記されています。

```python

```


## 参考文献
[1] https://platform.openai.com/docs/api-reference/ (2026-01-27アクセス)<br>

**Acknowledgement**  
This material was reviewed and refined with the assistance of ChatGPT (OpenAI) and Gemini(Google).

Kazuma Aoyama(kazuma-a@akamafu.com)