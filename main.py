import shutil
import asyncio
import argparse
from gtts import gTTS
from io import BytesIO

import ollama


async def speak(speaker, content):
    if speaker:
        tts = gTTS(content)
        tts_bytes = BytesIO()
        tts.write_to_fp(tts_bytes)
        p = await asyncio.create_subprocess_exec(speaker, stdin=asyncio.subprocess.PIPE)
        p.stdin.write(tts_bytes.getvalue())
        await p.communicate()


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--speak', default=False, action='store_true')
    args = parser.parse_args()

    speaker = None
    if args.speak:
        if say := shutil.which('say'):
            speaker = say
        elif (espeak := shutil.which('espeak')) or (espeak := shutil.which('espeak-ng')):
            speaker = espeak

    client = ollama.AsyncClient()

    messages = []

    while True:
        if content_in := input('>>> '):
            messages.append({'role': 'user', 'content': content_in})

            content_out = ''
            message = {'role': 'assistant', 'content': ''}
            async for response in await client.chat(model='tinydolphin', messages=messages, stream=True):
                if response['done']:
                    messages.append(message)

                content = response['message']['content']
                print(content, end='', flush=True)

                content_out += content
                if content in ['.', '!', '?', '\n']:
                    await speak(speaker, content_out)
                    content_out = ''

                message['content'] += content

            if content_out:
                await speak(speaker, content_out)
            print()


try:
    asyncio.run(main())
except (KeyboardInterrupt, EOFError):
    print("\nGoodbye!")
