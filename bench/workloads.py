import random

TOKENS_PER_WORD = 1.3

VOCAB = ("the server model token cache memory batch queue latency throughput "
         "kernel scheduler prefill decode layer weight attention request "
         "a of to in for with is are data time load rate fast slow").split()


def make_words(rng: random.Random, n_tokens: int) -> str:
    """Random words that add up to about n_tokens tokens."""
    n_words = round(n_tokens/ TOKENS_PER_WORD)                          # converted n_tokens to a word count using TOKENS_PER_WORD
    return " ".join(rng.choice(VOCAB) for _ in range(n_words))

def build_prompts(cfg: dict, n: int, seed: str) -> list[str]:
    """n prompts for one load point. Same cfg, n and seed give the same prompts."""
    rng = random.Random(seed)
    shared_tokens = cfg.get("shared_prefix_tokens", 0)
    # Built from its own fixed seed, so it's identical in every prompt and every run.
    shared = make_words(random.Random("shared-prefix"), shared_tokens) if shared_tokens else ""

    prompts = []
    for i in range(n):
        unique = f"Request {i}. " + make_words(rng, cfg["input_tokens"])
        if shared:
            prompt = shared + "\n\n" + unique                           # coding order
        else:
            prompt = unique                                             # chat/rag order
        prompts.append(prompt)
    return prompts
