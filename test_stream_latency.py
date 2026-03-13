import requests
import time
import json
import sys

def test_stream_latency(i):
    url = "http://localhost:8001/api/chat/stream"
    payload = {
        "question": "how to open a new bank account",
        "mode": "hybrid",
        "domain_id": "test-domain"
    }
    headers = {
        "Content-Type": "application/json"
    }

    print(f"\n--- RUN {i} ---")
    print(f"Sending request to {url}...")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()
        
        first_byte_time = None
        
        for line in response.iter_lines():
            if line:
                if not first_byte_time:
                    first_byte_time = time.time()
                    print(f"Time to First Byte (TTFB): {first_byte_time - start_time:.2f} seconds")
                
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    try:
                        data = json.loads(decoded_line[6:])
                        event_type = data.get('type')
                        if event_type == 'chunk':
                            continue # skip printing all chunks to keep output clean
                        print(f"[{time.time() - start_time:.2f}s] Event: {event_type}")
                        if event_type == 'status':
                            print(f"  -> {data.get('message')}")
                    except json.JSONDecodeError:
                        print(f"[{time.time() - start_time:.2f}s] Raw Data: {decoded_line[:50]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    for i in range(1, 3):
        test_stream_latency(i)

