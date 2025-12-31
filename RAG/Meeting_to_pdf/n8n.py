import requests
import os

N8N_WEBHOOK_URL = "https://sefohossam.app.n8n.cloud/webhook-test/6e1a9ff5-9b25-4f9d-ae09-19d918ba1bed"

def upload_to_n8n(file_path, webhook_url= N8N_WEBHOOK_URL):
    """
    Uploads a file to an n8n webhook via POST request.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    print(f"Uploading {file_path} to n8n...")

    try:
        # Open the file in binary mode
        with open(file_path, 'rb') as f:
            # 'data' matches the binary property name expected by n8n (default is usually 'data' or 'file')
            files = {'data': (os.path.basename(file_path), f, 'application/pdf')}

            # Send POST request
            response = requests.post(webhook_url, files=files)

        if response.status_code == 200:
            print("✅ Upload successful! Check your n8n workflow.")
        else:
            print(f"❌ Upload failed. Status: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
