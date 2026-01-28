import os, sys, time
from openai import OpenAI
from dotenv import load_dotenv

def generate_text(prompt, system_content):
    # .envファイル読み込み
    load_dotenv()
    # OpenAIクライアントを初期化
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
    
    try:
        stream = client.responses.create(
        model="gpt-5-nano",
        input=prompt,
        instructions=system_content,
        stream=True,
        reasoning={"effort": "minimal"},  #推論を最小化
        )

        buf = []
        last_flush = time.perf_counter()
        FLUSH_INTERVAL = 0.03  # 30msごとにまとめて表示

        for event in stream:
            if event.type == "response.output_text.delta":
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
    prompt = "動物のゾウとはどのようなものですか？"

    print("幼稚園児ver")
    system_content = "あなたは幼稚園児です。"
    generate_text(prompt, system_content)

    print("-"*50)

    print("専門家ver")
    system_content = "あなたは生物研究の専門家です。"
    generate_text(prompt, system_content)

if __name__ == "__main__":
    main()