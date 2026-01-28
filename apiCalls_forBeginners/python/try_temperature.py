import os, sys, time
from openai import OpenAI
from dotenv import load_dotenv

def generate_text(prompt, temperature=[0.1, 0.5, 1], run=3):
    # .envファイル読み込み
    load_dotenv()

    # OpenAIクライアントを初期化
    client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

    t0 = time.perf_counter()
    first_token_time = None
    
    for i in temperature:
        print("-"*40)
        print(f"temperature:{i}")
        for j in range(run):
            try:
                stream = client.responses.create(
                model="gpt-4.1-nano",
                input=prompt,
                stream=True,
                temperature=i,
                # reasoning={"effort": "minimal"},  # ← gpt-4.1-nanoでは外す
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

    generate_text("新しい航空会社のキャッチコピーを1つ考えて")

if __name__ == "__main__":
    main()
