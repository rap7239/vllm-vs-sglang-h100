import random

TOKENS_PER_WORD = 1.3

VOCAB = ("the server model token cache memory batch queue latency throughput "
         "kernel scheduler prefill decode layer weight attention request "
         "a of to in for with is are data time load rate fast slow").split()


def make_words(rng: random.Random, n_tokens: int) -> str:
    """Random words that add up to about n_tokens tokens."""
    n_words = round(n_tokens/ TOKENS_PER_WORD)  # converted n_tokens to a word count using TOKENS_PER_WORD
    return " ".join(rng.choice(VOCAB) for _ in range(n_words))
