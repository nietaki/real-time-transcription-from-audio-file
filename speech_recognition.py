import websockets
import asyncio
import base64
import json
import wave
from configure import auth_key
import sys

import pyaudio
 
FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()

if len(sys.argv) != 4:
    print("Usage: python3 speech_recognition.py <audio_file> <output_type: debug|label:utterance|label:word> <out_file>")
    sys.exit(1)

AUDIO_FILE, OUTPUT_TYPE, OUT_FILE = sys.argv[1:]

wf = wave.open(AUDIO_FILE, 'rb')
 
# the AssemblyAI endpoint we're going to hit
URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

 
async def send_receive():

    print(f'Connecting websocket to url ${URL}')

    async with websockets.connect(
        URL,
        extra_headers=(("Authorization", auth_key),),
        ping_interval=5,
        ping_timeout=20
    ) as _ws:
        with open(OUT_FILE, "w") as f:
            await asyncio.sleep(0.1)
            print("Receiving SessionBegins ...")

            session_begins = await _ws.recv()
            print(session_begins)
            print("Sending messages ...")


            async def send():
                while True:
                    try:
                        data = wf.readframes(FRAMES_PER_BUFFER)
                        data = base64.b64encode(data).decode("utf-8")
                        json_data = json.dumps({"audio_data":str(data)})
                        await _ws.send(json_data)

                    except websockets.exceptions.ConnectionClosedError as e:
                        print(e)
                        assert e.code == 4008
                        break

                    except Exception as e:
                        assert False, "Not a websocket 4008 error"

                    await asyncio.sleep(0.1)
                
                return True
            

            async def receive():
                while True:
                    try:
                        result_str = await _ws.recv()
                        payload = json.loads(result_str)
                        if 'message_type' in payload and payload['message_type'] == 'FinalTranscript':
                            if OUTPUT_TYPE == "debug":
                                start = payload['audio_start'] 
                                end = payload['audio_end'] 
                                f.write(str(start) + " -> " + str(end) + ": \n")
                                for word in payload['words']:
                                    start = word['start'] 
                                    end = word['end'] 
                                    text = word['text'] 
                                    f.write(" | " + str(start) + " -> " + str(end) + ": " + text + "\n")
                            elif OUTPUT_TYPE == "label:utterance":
                                text = ""
                                for word in payload['words']:
                                    text += word['text']
                                    text += " "
                                if not text:
                                    text = "<empty>"
                                start = payload['audio_start'] / 1000
                                end = payload['audio_end'] / 1000
                                f.write(str(start) + "\t" + str(end) + "\t" + text + "\n")
                            elif OUTPUT_TYPE == "label:word":
                                for word in payload['words']:
                                    start = word['start'] / 1000
                                    end = word['end'] / 1000
                                    text = word['text'] 
                                    f.write(str(start) + "\t" + str(end) + "\t" + text + "\n")
                            f.flush()

                    except websockets.exceptions.ConnectionClosedError as e:
                        print(e)
                        assert e.code == 4008
                        break

                    except Exception as e:
                        assert False, "Not a websocket 4008 error"
            
            send_result, receive_result = await asyncio.gather(send(), receive())

while True:
    asyncio.run(send_receive())
