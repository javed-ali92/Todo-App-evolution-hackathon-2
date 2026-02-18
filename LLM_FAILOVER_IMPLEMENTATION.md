# Automatic LLM Failover Implementation

## Overview

Implemented automatic failover system for the chatbot backend with the following configuration:

**Primary LLM:** Gemini (gemini-2.0-flash)
**Fallback LLM:** Groq (llama-3.1-8b-instant)

## How It Works

When a user sends a message:

1. **Primary Attempt:** System tries Gemini API first
2. **Error Detection:** If Gemini fails with retriable error (quota, rate limit, timeout, unavailable)
3. **Automatic Failover:** System automatically retries with Groq
4. **Response:** User receives response from whichever LLM succeeds

## Configuration

### Environment Variables (.env)

```bash
# Primary LLM
GEMINI_API_KEY="your-gemini-api-key-here"
GEMINI_MODEL="gemini-2.0-flash"

# Fallback LLM
GROQ_API_KEY="your-groq-api-key-here"
GROQ_MODEL="llama-3.1-8b-instant"

# Priority setting
PRIMARY_LLM="gemini"  # Options: "gemini" or "groq"
```

### Reversing Priority

To make Groq primary and Gemini fallback:

```bash
PRIMARY_LLM="groq"
```

## Retriable Errors

The system automatically retries with fallback LLM when detecting:

- `quota` - API quota exceeded
- `rate` - Rate limit hit
- `limit` - Request limit reached
- `429` - HTTP 429 status code
- `unavailable` - Service unavailable
- `timeout` - Request timeout
- `resource_exhausted` - Resources exhausted

## Implementation Details

### Files Modified

1. **backend/src/chatbot_agents/gemini_connection.py**
   - Added Groq client configuration
   - Added `get_fallback_config()` function
   - Updated `get_config()` to respect PRIMARY_LLM setting

2. **backend/src/chatbot_agents/sdk_agent.py**
   - Modified `process_message()` to implement failover logic
   - Added error detection and retry mechanism
   - Added logging for failover events

3. **backend/.env**
   - Added GROQ_API_KEY
   - Added GROQ_MODEL
   - Added PRIMARY_LLM setting

### Code Flow

```python
async def process_message(user_id, message):
    try:
        # Try primary LLM (Gemini)
        result = await Runner.run(agent, message, primary_config)
        return result

    except Exception as primary_error:
        if is_retriable_error(primary_error) and fallback_config:
            logger.warning("Primary failed, switching to fallback")

            try:
                # Retry with fallback LLM (Groq)
                result = await Runner.run(agent, message, fallback_config)
                return result

            except Exception as fallback_error:
                logger.error("Both LLMs failed")
                return error_response
```

## Logging

The system logs failover events:

```
INFO: Processing message for user 1 with primary LLM
WARNING: Primary LLM failed (RateLimitError), switching to fallback LLM
WARNING: Primary error: Error code: 429 - quota exceeded...
INFO: Retrying with fallback LLM for user 1
INFO: Fallback LLM succeeded
```

## Testing Results

### Test 1: Simple Message
```
Input: "Hello, how are you?"
Primary: Gemini (FAILED - quota exceeded)
Fallback: Groq (SUCCESS)
Response: "I'm an assistant designed to help you manage your tasks..."
```

### Test 2: Task Creation
```
Input: "Add a task to test the failover system"
Primary: Gemini (FAILED - quota exceeded)
Fallback: Groq (SUCCESS)
Result: Task created successfully with tool execution
```

## Benefits

1. **High Availability:** System continues working even when primary LLM fails
2. **Transparent:** Users don't see errors, just get responses
3. **Cost Optimization:** Can use cheaper fallback when primary is unavailable
4. **Flexible:** Easy to switch primary/fallback via env variable
5. **Resilient:** Handles multiple failure scenarios automatically

## Monitoring

Check logs for failover events:

```bash
grep "switching to fallback" backend/logs/*.log
```

## Production Recommendations

1. **Monitor Failover Rate:** Track how often fallback is used
2. **Alert on Both Failures:** Set up alerts when both LLMs fail
3. **Cost Tracking:** Monitor API usage for both providers
4. **Performance:** Groq is faster but may have different quality
5. **Quota Management:** Upgrade Gemini to paid tier to reduce failovers

## API Specifications

### Gemini API
- Endpoint: `https://generativelanguage.googleapis.com/v1beta/openai/`
- Model: `gemini-2.0-flash`
- Free Tier: Limited requests per day/minute

### Groq API
- Endpoint: `https://api.groq.com/openai/v1/`
- Model: `llama-3.1-8b-instant`
- Speed: Very fast inference
- Quality: Good for task management use case

## Troubleshooting

### Both LLMs Failing
- Check API keys are valid
- Verify network connectivity
- Check quota limits on both providers

### Fallback Not Triggering
- Verify GROQ_API_KEY is set in .env
- Check error is in retriable list
- Review logs for error type

### Wrong LLM Being Used
- Check PRIMARY_LLM setting in .env
- Restart backend after .env changes
- Verify configuration loading in logs

## Future Enhancements

1. Add more fallback providers (Claude, OpenAI)
2. Implement circuit breaker pattern
3. Add automatic quota monitoring
4. Implement smart routing based on message type
5. Add fallback chain (Gemini → Groq → OpenAI)
