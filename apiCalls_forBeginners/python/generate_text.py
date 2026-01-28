import os, sys, time
from openai import OpenAI
from dotenv import load_dotenv

def generate_text(prompt):
    # .envファイル読み込み
    load_dotenv()
    # OpenAIクライアントを初期化
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
    
    try:
        stream = client.responses.create(
        model="gpt-5-nano",
        input=prompt,
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
    generate_text("格言を一つ教えてください。")

if __name__ == "__main__":
    main()