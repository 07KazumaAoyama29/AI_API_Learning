# API呼び出しの基本構文と動作確認
## 基本プログラム

Open AI APIを使用するときは、公式が提供するライブラリを使うことで、**効率的かつ安全**にAPIを呼び出すことができる。

まずは、公式ライブラリを使った、**シンプルなテキスト生成を行うプログラム**を作成する。

environmental_setup で作成したプログラムとほぼ同じ。**関数化**をして安全性を高めているだけ。

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
環境変数(プログラムが実行される環境において、外部から設定される変数)から安全に API キーを取得することで、**安全に認証情報を管理**できる。

ここでいう環境変数とは

```python
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
```

のこと。

- message パラメータ:
会話形式の入力を**辞書形式**で指定する。AIの**振る舞い**を柔軟に**制御**できる。

- 例外処理:
try, exceptの例外処理を書くことで、**ネットワークエラーやレート制限などの問題**に**自動で**対処できるようになる。

## systemロールの比較実験
systemロールに技術専門家と初心者向けアシスタントという異なる設定を与え、
**同じ質問に対する回答がどう変わるか**を比較する。

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

同じ質問でも、**ロール**によって**応答の詳しさや語調**がかなり変わる。


## 出力制御パラメータについて

API には、 **AI の応答品質**を左右する、重要なパラメータが複数用意されている。

プロンプトの工夫(プロンプトエンジニアリング)だけではなく、これらの**パラメータを調整**することで
より**精度・品質の高い出力**を得られることができる。

### GPT-5-nanoで指定可能なパラメータ

以下は model: "gpt-5-nano" で client.responses.create(...) に渡せる
(= Responses APIのCreateで受け付けられる)リクエストボディの**トップレベル引数**の一覧[[1]](https://platform.openai.com/docs/api-reference/)

```txt
model, input, instructions, previous_response_id, conversation, prompt, text, reasoning（※gpt-5系のみ）, tools, tool_choice, parallel_tool_calls
max_tool_calls, max_output_tokens, truncation, stream, stream_options, include, background, store, metadata, service_tier, safety_identifier
prompt_cache_key, prompt_cache_retention, user（Deprecated。prompt_cache_key / safety_identifier へ移行推奨）
```

・・・という感じで**大量**に設定可能。

以下では、代表的なものや便利なもの、出力に影響が大きいものを**実際のコード付き**で紹介する。

### ①temperature(創造性の制御)

temperature は **出力の安定性** と **多様性のバランス** を調整するパラメータ。

低い場合は **安定した答え** 、高い場合は **表現に幅が出やすくなる** (実行するごとに出力が変わる)。

AI の パラメータの中で、一番有名なのではないか。(**※完全に主観です。**)

しかし、GPT-5-nano では temperature は **設定不可** になっている。

OpenAIのモデルガイド(2026-01-27アクセス)では、

temperature / top_p / logprobs は **GPT-5.2 で reasoning.effort: "none" のときだけ** サポート

それ以外の reasoning effort（none以外）や、古い GPT-5 系（gpt-5, gpt-5-mini, gpt-5-nano）にこれらを含めると **エラー** になる

と明記されている。

逆に、 **GPT-4.1-nanoなどのモデルでは、temperature　の設定が可能。**

なぜ新しいバージョン(GPT=5-nano)の方が temperature のような中核パラメータが使えないのかというと、
GPT-5系（特に古い gpt-5 / mini / nano）が **推論を前提** にしていて、生成のしかたが“1回サンプルして終わり”じゃないから。

推論モードでは、内部で「考えるためのトークン」「道具呼び出し」「複数段の生成・整形」みたいなプロセスが絡むので、
temperature をそのまま露出すると **品質が不安定** になったり、 **意図しない揺らぎ** が増えて“推論の強み”が崩れる、という設計判断になっているイメージ。

実際、 temperature の代替として **reasoning.effort（考える量）、text.verbosity（冗長さ）、max_output_tokens（長さ）** を使ってね、という案内がある。

上記のプログラムでは reasoning={"effort": "minimal"} と設定していたので、 temperature が低い設定でやっていたことになる。text.verbosity（冗長さ）、max_output_tokens（長さ）については後述する。

temperatureを設定したい場合は、**gpt-5 / mini / nano以外のモデル**を使う必要がある。

以下のプログラムでは、**gpt-4.1-nano** を使う。

既存のプログラムの stream の引数を以下に書き換えるだけ。

```python
stream = client.responses.create(
    model="gpt-4.1-nano",
    input=prompt,
    stream=True,
    temperature=0.1,
    # reasoning={"effort": "minimal"},  # ← gpt-4.1-nanoでは外す
)
```









### text

「どれだけ詳しく書くか」(verbosity) や、JSON/構造化出力 の土台。温度の代替として “話し方” を制御できる。
使い方（verbosity）

```python
text={"verbosity": "low"}  # "low"|"medium"|"high"
```

### max_output_tokens

コスト・レイテンシ・暴走防止の最重要安全弁。可視出力だけでなく reasoning tokens も含めた上限。
使い方

```python
max_output_tokens=800
```

### tools

エージェント化の入口。「Web検索」「ファイル検索」「自作関数」など、モデルが呼べる道具を宣言する。
使い方（例: 自作関数ツール）

```python
tools=[{"type":"function","name":"lookup_user","description":"…","parameters":{...}}]
```

### tool_choice

ツールを 自動で選ばせる / 使わせない / 特定ツールを強制 ができ、コストと挙動が安定する。
使い方（例）

```python
tool_choice="auto"     # 自動（デフォルト的）
# tool_choice="none"   # ツール禁止（可能な場合）
# tool_choice={"type":"function","name":"lookup_user"}  # 強制（可能な場合）
```

### previous_response_id


マルチターンを簡単につなぐ“ひも”。会話状態を引き継ぎたいときに便利（conversation と同時には使えない）。
使い方

```python
previous_response_id=prev.id
```



### store: 
レスポンスを保存して後で取得できる。推論系では store:true + previous_response_id が推奨される場面がある。

### truncation: 
入力がコンテキスト上限を超えるときの挙動（auto なら古い方から落として続行、disabled なら400で失敗）。


## 参考文献
[1] https://platform.openai.com/docs/api-reference/ (2026-01-27アクセス)<br>

**Acknowledgement**  
This material was reviewed and refined with the assistance of ChatGPT (OpenAI) and Gemini(Google).

Kazuma Aoyama(kazuma-a@akamafu.com)