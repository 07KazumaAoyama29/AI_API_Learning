import os, sys, time
from openai import OpenAI
from dotenv import load_dotenv

def main():
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = "プログラミングにおける、環境構築って英語でなんて言うの？"

    t0 = time.perf_counter()
    first_token_time = None

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

if __name__ == "__main__":
    main()
