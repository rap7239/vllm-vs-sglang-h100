import asyncio
import json
import time

import httpx


async def one_request(client, base_url, api_key, model, prompt, max_tokens):
    """Send one streaming chat request and time every token."""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "ignore_eos": True,         #Keep generating until max_tokens: same work for every server
        "temperature": 0.0,
        "stream": True,             #send tokens as they are made
        "stream_options": {"include_usage": True},  #last message carries exact token counts
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    token_times = []
    usage = None
    start = time.perf_counter()     #a stopwatch clock, not the time of day

    async with client.stream("POST", f"{base_url}/v1/chat/completions",
                      json=payload, headers=headers, timeout=300) as resp:
        resp.raise_for_status()
        async for line in resp.aiter_lines():
            if not line.startswith("data:"):
                continue            #skip blank keep-alive lines
            data = line[5:].strip()
            if data == "[DONE]":
                break
            chunk = json.loads(data)
            if chunk.get("usage"):
                usage = chunk["usage"]
            choices = chunk.get("choices") or []
            if choices and choices[0].get("delta", {}).get("content"):
                token_times.append(time.perf_counter())

    end = time.perf_counter()
    out = usage["completion_tokens"] if usage else None
    tpot_ms = (end - token_times[0]) * 1000 / (out - 1) if token_times and out and out > 1 else None

    return {
        "ttft_ms": (token_times[0] - start) * 1000 if token_times else None,
        "itl_ms": [(b - a) * 1000 for a, b in zip(token_times, token_times[1:])],
        "e2e_ms": (end - start) * 1000,
        "tpot_ms": tpot_ms,
        "input_tokens": usage["prompt_tokens"] if usage else None,
        "output_tokens": usage["completion_tokens"] if usage else None,
    }

def make_client():
    """An httpx client with no connection cap, so only our own load settings limit requests in flight."""
    limits = httpx.Limits(max_connections=None, max_keepalive_connections=None)
    return httpx.AsyncClient(limits=limits)

async def run_concurrency(client, base_url, api_key, model, prompts, max_tokens, concurrency):
    """Keep 'concurrency' requests in flight until every prompt has been answered."""
    sem = asyncio.Semaphore(concurrency)

    async def limited(prompt):
        async with sem:
            return await one_request(client, base_url, api_key, model, prompt, max_tokens)

    start = time.perf_counter()
    results = await asyncio.gather(*(limited(p) for p in prompts))
    wall_s = time.perf_counter() - start
    return results, wall_s