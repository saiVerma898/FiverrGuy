import requests
import json
import argparse
import sys
import time
import base64
import os

def test_endpoint(endpoint_url, api_key, payload_file):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        with open(payload_file, 'r') as f:
            payload = json.load(f)
    except Exception as e:
        print(f"Error loading payload file: {e}")
        return

    print(f"Sending request to {endpoint_url}...")
    
    # 1. Initiate Job (RunSync) or Async?
    # The user provided ".../run", which usually returns a job ID (async).
    # ".../runsync" waits.
    # We will try runsync first if the URL ends with runsync, otherwise we handle async.
    
    if endpoint_url.endswith("/runsync"):
         response = requests.post(endpoint_url, headers=headers, json=payload, timeout=600)
         print(f"Status Code: {response.status_code}")
         print("Response:")
         data = response.json()
         print(json.dumps(data, indent=2))
         save_output_image(data.get("output"), "runsync_output.png")
    else:
        # Async run
        response = requests.post(endpoint_url, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
             print(f"Error ({response.status_code}): {response.text}")
             return
             
        job_data = response.json()
        job_id = job_data.get("id")
        print(f"Job started with ID: {job_id}")
        
        # Poll for status
        status_url = endpoint_url.replace("/run", f"/status/{job_id}")
        
        while True:
            time.sleep(2)
            status_resp = requests.get(status_url, headers=headers)
            status_data = status_resp.json()
            status = status_data.get("status")
            print(f"Status: {status}")
            
            if status == "COMPLETED":
                print("Job Completed!")
                print("Output:")
                output = status_data.get("output")
                print(json.dumps(output, indent=2))
                save_output_image(output, "run_output.png")
                break
            elif status == "FAILED":
                print("Job Failed.")
                print("Error:")
                print(status_data.get("error"))
                break

def save_output_image(output, output_filename):
    if not isinstance(output, dict):
        print("No structured output object returned; skipping image decode.")
        return

    image_b64 = output.get("image")
    if not image_b64:
        print("No 'image' key found in output; skipping image decode.")
        return

    try:
        image_bytes = base64.b64decode(image_b64, validate=True)
    except Exception as exc:
        print(f"Failed to decode output.image as base64: {exc}")
        return

    with open(output_filename, "wb") as file:
        file.write(image_bytes)

    print(f"Decoded output image saved to: {os.path.abspath(output_filename)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test RunPod Endpoint")
    parser.add_argument("api_key", help="Your RunPod API Key")
    parser.add_argument("--url", default="https://api.runpod.ai/v2/mi9rxwoaz232lv/run", help="Endpoint URL")
    parser.add_argument("--payload", default="postman_example.json", help="Path to payload JSON")
    
    args = parser.parse_args()
    
    test_endpoint(args.url, args.api_key, args.payload)
