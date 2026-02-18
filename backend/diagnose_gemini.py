"""
Diagnostic script to verify Gemini API configuration and connectivity.
Tests each component step-by-step to identify the real issue.
"""
import os
import sys
from pathlib import Path
from openai import OpenAI
import json

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

print("=" * 80)
print("GEMINI API DIAGNOSTIC TOOL")
print("=" * 80)

# Step 1: Verify .env file location and loading
print("\n[STEP 1] Checking .env file...")
env_file = backend_path / ".env"
print(f"  [OK] .env path: {env_file}")
print(f"  [OK] .env exists: {env_file.exists()}")

if env_file.exists():
    with open(env_file, 'r') as f:
        env_content = f.read()
    print(f"  [OK] .env size: {len(env_content)} bytes")
    # Check if GEMINI_API_KEY is in file
    if "GEMINI_API_KEY" in env_content:
        print("  [OK] GEMINI_API_KEY found in .env file")
    else:
        print("  [FAIL] GEMINI_API_KEY NOT found in .env file")

# Step 2: Load environment variables
print("\n[STEP 2] Loading environment variables...")
from dotenv import load_dotenv
load_dotenv(env_file)

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

print(f"  [OK] GEMINI_MODEL: {model}")

if api_key:
    # Mask the key for security
    masked_key = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 14 else "***"
    print(f"  [OK] GEMINI_API_KEY loaded: {masked_key}")
    print(f"  [OK] Key length: {len(api_key)} characters")
    print(f"  [OK] Key starts with: {api_key[:7]}")
else:
    print("  [FAIL] GEMINI_API_KEY is None or empty!")
    sys.exit(1)

# Step 3: Verify OpenAI client configuration
print("\n[STEP 3] Configuring OpenAI client for Gemini...")
base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
print(f"  [OK] Base URL: {base_url}")
print(f"  [OK] API Key (first 10 chars): {api_key[:10]}")

try:
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    print("  [OK] OpenAI client created successfully")
except Exception as e:
    print(f"  [FAIL] Failed to create client: {e}")
    sys.exit(1)

# Step 4: Test API connectivity with minimal request
print("\n[STEP 4] Testing API connectivity...")
print(f"  [INFO] Sending test request to {base_url}chat/completions")
print(f"  [INFO] Model: {model}")
print(f"  [INFO] Message: 'Hello'")

try:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": "Hello"}
        ],
        max_tokens=10,
        timeout=15
    )
    print("  [SUCCESS] API request successful!")
    print(f"  [SUCCESS] Response: {response.choices[0].message.content}")
    print("\n" + "=" * 80)
    print("[SUCCESS] DIAGNOSIS: Gemini API is working correctly!")
    print("=" * 80)

except Exception as e:
    print(f"  [FAIL] API request failed!")
    print("\n[ERROR DETAILS]")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error message: {str(e)}")

    # Try to extract more details
    if hasattr(e, 'response'):
        print(f"\n[HTTP RESPONSE]")
        print(f"  Status code: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
        try:
            print(f"  Response body: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
        except:
            pass

    if hasattr(e, 'status_code'):
        print(f"  Status code: {e.status_code}")

    if hasattr(e, 'body'):
        print(f"  Body: {e.body}")

    # Check for specific error types
    if "429" in str(e) or "quota" in str(e).lower():
        print("\n[DIAGNOSIS]")
        print("  [FAIL] Issue: API quota exceeded")
        print("  [FAIL] The API key has exhausted its free tier quota")
        print("  [FAIL] Solution: Use a different API key or upgrade to paid tier")
    elif "401" in str(e) or "unauthorized" in str(e).lower():
        print("\n[DIAGNOSIS]")
        print("  [FAIL] Issue: Invalid API key")
        print("  [FAIL] The API key is not valid or has been revoked")
        print("  [FAIL] Solution: Generate a new API key from Google AI Studio")
    elif "403" in str(e) or "forbidden" in str(e).lower():
        print("\n[DIAGNOSIS]")
        print("  [FAIL] Issue: API access forbidden")
        print("  [FAIL] The API key may not have permission to use this model")
        print("  [FAIL] Solution: Check API key permissions in Google AI Studio")
    elif "404" in str(e):
        print("\n[DIAGNOSIS]")
        print("  [FAIL] Issue: Endpoint not found")
        print("  [FAIL] The base URL or model name may be incorrect")
        print(f"  [FAIL] Current base URL: {base_url}")
        print(f"  [FAIL] Current model: {model}")
    else:
        print("\n[DIAGNOSIS]")
        print("  [FAIL] Issue: Unknown error")
        print("  [FAIL] Check the error details above")

    print("\n" + "=" * 80)
    sys.exit(1)

# Step 5: Verify the configuration matches task_agent.py
print("\n[STEP 5] Verifying configuration matches task_agent.py...")
try:
    from src.agents.task_agent import TaskAgent
    from src.mcp.server import mcp_server

    agent = TaskAgent(mcp_server)
    print(f"  [OK] TaskAgent initialized")
    print(f"  [OK] Agent model: {agent.model}")
    print(f"  [OK] Agent API key (first 10): {agent.api_key[:10]}")
    print(f"  [OK] Agent base URL: {agent.client.base_url}")

    if agent.api_key == api_key:
        print("  [OK] API keys match!")
    else:
        print("  [FAIL] API keys DO NOT match!")
        print(f"    .env key: {api_key[:10]}...")
        print(f"    Agent key: {agent.api_key[:10]}...")

except Exception as e:
    print(f"  [FAIL] Failed to verify TaskAgent: {e}")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
