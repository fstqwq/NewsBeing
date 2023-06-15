
from transformers import (
    AutoTokenizer,
    LEDConfig,
    LEDForConditionalGeneration,
)

import torch

def get_summary(docs, model, tokenizer):
    global PAD_TOKEN_ID, DOCSEP_TOKEN_ID
    input_ids = []
    max_len = 1024 // len(docs)
    for doc in docs:
        doc = doc.replace("\n", " ")
        doc = " ".join(doc.split())
        input_ids.extend(
                tokenizer.encode(
                    doc,
                    truncation=True,
                    max_length= max_len,
                )[1:-1]
            )
        input_ids.append(DOCSEP_TOKEN_ID)
    input_ids = (
            [tokenizer.bos_token_id]
            + input_ids
            + [tokenizer.eos_token_id]
        )
    input_ids = input_ids + (max_len - len(input_ids)) * [PAD_TOKEN_ID]
    input_ids = torch.tensor(input_ids).long().view(1,-1)
    # print(input_ids)
    global_attention_mask = torch.zeros_like(input_ids).to(input_ids.device)
    global_attention_mask[:, 0] = 1
    global_attention_mask[input_ids == DOCSEP_TOKEN_ID] = 1

    import time
    with torch.no_grad():
        begin = time.time()
        generated_ids = model.generate(
                input_ids=input_ids,
                global_attention_mask=global_attention_mask,
                use_cache=True,
                max_length=128, # 可以改summary长度
                num_beams=1  #按需调整
            )
        end = time.time()
        print('summary time:', end-begin)
    # print(generated_ids)
    generated_str = tokenizer.batch_decode(
            generated_ids.tolist(), skip_special_tokens=True
        )[0]
    # print('generated str:', generated_str)
    return generated_str

def ai_worker(config, input, output):
    summary_path = config["summary_path"]
    tokenizer = AutoTokenizer.from_pretrained(summary_path)
    config = LEDConfig.from_pretrained(summary_path)
    summary_model = LEDForConditionalGeneration.from_pretrained(summary_path, config=config)
    global PAD_TOKEN_ID, DOCSEP_TOKEN_ID
    PAD_TOKEN_ID = tokenizer.pad_token_id
    DOCSEP_TOKEN_ID = tokenizer.convert_tokens_to_ids("<doc-sep>")
    import signal
    def on_exit(signum, frame):
        exit(0)
    signal.signal(signal.SIGINT, on_exit)
    while True:
        task = input.get()
        if task is None:
            break
        try:
            ty, query = task
            if ty == "summary":
                summary = get_summary(query, summary_model, tokenizer)
                output.put(summary)
            elif ty == "bye":
                break
            else:
                raise ValueError("Unknown task type")
        except Exception as e:
            print(f"query = {query}, error = {e}")
            output.put(e)

if __name__ == "__main__":
    config = {
        "summary_path": "ai/PRIMERA-multinews"
    }
    from multiprocessing import Manager, Process
    manager = Manager()
    input = manager.Queue()
    output = manager.Queue()
    process = Process(target=ai_worker, args=(config, input, output))        
    process.start()

    docs = [
        """I Really Want to Stay at Your House
Song by Hallie Coggins and Rosa Walton
OverviewLyricsVideosListen
Lyrics
I couldn't wait for you to come clear the cupboards
But now you're going to leave with nothing but a sign
Another evening I'll be sitting reading in between your lines
Because I miss you all the time
So, get away
Another way to feel what you didn't want yourself to know
And let yourself go
You know you didn't lose your self-control
Let's start at the rainbow
Turn away
Another way to be where you didn't want yourself to go
Let yourself go
Is that a compromise?
So, what do you wanna do, what's your point-of-view?
There's a party soon, do you wanna go?
A handshake with you, what's your point-of-view?
I'm on top of you, I don't wanna go
'Cause I really wanna stay at your house
And I hopе this works out
But you know how much you broke me apart
I'm done with you, I'm ignoring you
I don't wanna know
And I'm awarе that you were lying in the gutter
'Cause I did everything to be there by your side-ide
So, when you tell me I'm the reason I just can't believe the lies
And why do I so want to call you (call you, call you, call you)
So, what do you wanna do, what's your point-of-view?
There's a party soon, do you wanna go?
A handshake with you, what's your point-of-view?
I'm on top of you, I don't wanna go
'Cause I really wanna stay at your house
And I hope this works out
But you know how much you broke me apart
I'm done with you, I'm ignoring you
I don't wanna know
Oh
Oh-oh, oh-oh-oh
I don't know why I'm no one
So, get away
Another way to feel what you didn't want yourself to know
And let yourself go
You know you didn't lose your self-control
Let's start at the rainbow
Turn away
Another way to be where you didn't want yourself to go
Let yourself go
Is that a compromise?
So, what do you wanna do, what's your point-of-view?
There's a party soon, do you wanna go?
A handshake with you, what's your point-of-view?
I'm on top of you, I don't wanna go
'Cause I really wanna stay at your house
And I hope this works out
But you know how much you broke me apart
I'm done with you, I'm ignoring you
I don't wanna know"""]
    input.put(("summary", docs))
    print(output.get())
    input.put(("bye", None))