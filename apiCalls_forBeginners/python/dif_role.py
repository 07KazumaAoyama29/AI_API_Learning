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
