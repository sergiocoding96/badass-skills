---
name: hermes-mlops-inference
description: Complete LLM inference workflows — serving with vLLM, GGUF quantization for CPU/GPU, structured output with Outlines and Guidance, and model surgery (ablation/removal of refusal layers). Use when serving LLMs, quantizing models, or extracting/ablating model layers.
category: mlops/inference
---

# Hermes MLOps Inference

Complete LLM inference workflows — vLLM serving, GGUF quantization, structured output, and model layer ablation.

**Trigger conditions**: need to serve an LLM with high throughput, quantize a model for CPU inference, extract model weights, or remove refusal/hallucination layers from a model.

---

## Skill Map

| Task | Use This Skill |
|------|---------------|
| High-throughput LLM serving with vLLM | → `serving-llms-vllm` subsection below |
| GGUF quantization for CPU/efficient GPU inference | → `gguf-quantization` subsection below |
| Structured JSON/regex output with Outlines | → `outlines` subsection below |
| Structured output with Guidance grammar | → `guidance` subsection below |
| Ablate/remove refusal layers from a model | → `obliteratus` subsection below |
| llama.cpp local inference + HF Hub model discovery | → `llama-cpp` subsection below |

---

## serving-llms-vllm

Serve LLMs with high throughput using vLLM's PagedAttention.

### When to Use
- Production inference with high throughput needs
- Batching multiple requests efficiently
- OpenAI-compatible API endpoint

### Installation
```bash
pip install vllm
```

### Basic Server Launch
```bash
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.1-8B-Instruct \
  --tensor-parallel-size 2 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 8192 \
  --port 8000
```

### OpenAI-Compatible API Usage
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2?"}
    ],
    temperature=0.7,
    max_tokens=512
)

print(response.choices[0].message.content)
```

### Multi-GPU Configuration
```bash
# 2 GPUs
--tensor-parallel-size 2

# 4 GPUs
--tensor-parallel-size 4

# 8 GPUs (multi-node)
--tensor-parallel-size 8 \
--rank 0 \
--master-port 29500
```

### Quantization with vLLM
```bash
# AWQ quantization (recommended for speed + quality)
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.1-8B-Instruct-AWQ \
  --quantization awq

# GPTQ quantization
--quantization gptq
```

### Batching and Throughput
```bash
# Increase batch size for higher throughput
--max-num-batched-tokens 32768
--max-num-seqs 256

# For long context
--max-model-len 32768
```

### Common Issues

**Out of memory:**
- Reduce `--gpu-memory-utilization` (0.9 → 0.7)
- Reduce `--max-model-len`
- Use quantization (AWQ/GPTQ)

**Low throughput:**
- Increase `--max-num-batched-tokens`
- Increase `--max-num-seqs`
- Use tensor parallelism for larger models

---

## gguf-quantization

GGUF format and llama.cpp quantization for efficient CPU/GPU inference.

### When to Use
- Running models on CPU
- Memory-constrained environments
- Fast local inference without GPU

### What is GGUF?
GGUF (formerly GGML) is a quantization format designed for CPU+GPU inference via llama.cpp. It supports multiple quantization levels (Q2_K, Q4_K, Q5_K, Q6_K, Q8_0).

### Quantization Levels

| Level | Size (vs fp16) | Quality | Best For |
|-------|----------------|---------|----------|
| Q8_0 | ~50% | Highest (near fp16) | GPU when size matters less |
| Q6_K | ~40% | Very high | Good balance |
| Q5_K | ~33% | High | Memory constrained |
| Q4_K | ~25% | Good | Memory tight |
| Q3_K | ~20% | Medium | Very tight memory |
| Q2_K | ~15% | Low | Extreme compression |

### Quantize with llama.cpp
```bash
# Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Build
cmake -B build
cmake --build build --config Release

# Quantize a model
./build/bin/llama-quantize \
  --model /path/to/model.gguf \
  --output /path/to/model-Q4_K.gguf \
  --separator !Q4_K
```

### Using HF Hub GGUF Models
Many models on HF have pre-quantized GGUF versions:

```python
from llama_cpp import Llama
from huggingface_hub import hf_hub_download

# Download GGUF file
model_path = hf_hub_download(
    repo_id="TheBloke/Llama-3-8B-Instruct-GGUF",
    filename="llama-3-8b-instruct-q4_k_m.gguf"
)

# Load with llama-cpp-python
llm = Llama(
    model_path=model_path,
    n_ctx=4096,
    n_gpu_layers=35  # Layers to offload to GPU
)

output = llm(
    "What is 2+2?",
    max_tokens=256,
    echo=True
)
```

### HF-to-GGUF Conversion
```bash
# Convert HuggingFace model to GGUF
python convert-hf-to-gguf.py \
  --model /path/to/hf/model \
  --outfile /path/to/output.gguf \
  --outtype q4_k
```

### Common Issues

**Model won't load:**
- Check if GGUF file is complete (check file size)
- Verify quantization type is supported by your llama.cpp version

**Slow inference:**
- Increase `n_gpu_layers` to offload more layers to GPU
- Use a higher quantization level (Q5_K or Q6_K)
- Increase `n_ctx` if you're truncating context

**Wrong quantization size:**
- The file size should roughly match expected ratio (Q4_K ≈ 25% of fp16)

---

## outlines

Structured JSON/regex/Pydantic generation with Outlines.

### When to Use
- Need guaranteed valid JSON output
- Regex-constrained generation
- Pydantic model-constrained generation

### Installation
```bash
pip install outlines
```

### Basic JSON Generation
```python
import outlines

# Simple JSON schema
prompt = """Generate a user profile."""

result = outlines.generate.json(
    model,
    {"name": str, "age": int, "email": str}
)(prompt)

# result is a dict with name, age, email
```

### Pydantic Model Generation
```python
from pydantic import BaseModel
from typing import List

class Article(BaseModel):
    title: str
    content: str
    tags: List[str]
    published: bool

prompt = "Write an article about AI."

result = outlines.generate.json(model, Article)(prompt)
# result is an Article pydantic instance
```

### Regex-Constrained Generation
```python
import re

# Constrain to a specific format
pattern = r"\[.*?\]\(https://.*?\)"

result = outlines.generate.regex(
    model,
    pattern
)("List some links in markdown format: ")
```

### Streaming
```python
choices = outlines.generate.json(model, Article)(
    "Write an article about AI.",
    stream=True
)

for chunk in choices:
    print(chunk, end="", flush=True)
```

### Integration with vLLM
```python
from vllm import LLM
import outlines

# vLLM model
llm = LLM(model="meta-llama/Llama-3.1-8B-Instruct")

# Create Outlines engine
engine = outlines.llm.vllm.VLLMEngine(llm)

# Generate with JSON schema
result = outlines.generate_json(
    engine,
    {"name": str, "age": int}
)("Generate a fake person.")
```

### Pitfalls
- Complex schemas can make generation very slow (Outlines tries to make every token valid)
- Some regex patterns are too restrictive and cause the model to fail to complete
- For very complex schemas, consider using 2-pass generation (coarse then refine)

---

## guidance

Control LLM output with regex and grammars using Guidance.

### When to Use
- Token-level control over generation
- Multi-step generation with state
- Regex or grammar-constrained output

### Installation
```bash
pip install guidance
```

### Basic Usage
```python
import guidance

# Define a prompt with structural control
prompt = guidance("""The animal {{select 'name' options=animals}} says:
{{~#each sounds~}}
{{name}} says {{this}}!
{{~/each}}""")

result = prompt(
    name=guidance.llm.OpenAI("gpt-4"),
    animals=["cat", "dog", "cow"],
    sounds=["meow", "woof", "moo"]
)
```

### Grammar-Constrained Generation
```python
import guidance

# Force valid JSON with a grammar
grammar = r'''
{
    "name": str,
    "age": int,
    "email": str
}
'''

prompt = guidance("""Generate a user profile in JSON format:
{{gen 'output' grammar=grammar}}""")

result = prompt(
    grammar=grammar,
    ...
)
```

### Tool Use / Function Calling
```python
import guidance

prompt = guidance("""Consider the following conversation:
{{#each history}}
- {{role}}: {{content}}
{{/each}}

Now respond as {{agent_name}}.
{{gen 'response' max_tokens=200}}""")

# Multi-step with memory
history = []
for turn in conversation:
    history.append({"role": "user", "content": turn})
    result = prompt(agent_name="Assistant", history=history)
    history.append({"role": "assistant", "content": result["response"]})
```

### Regex Masking
```python
# Mask out certain patterns during generation
prompt = guidance("""Translate to French:
English: {{input}}
French: {{gen 'french' stop="\\n"}}""")
```

### Comparison: Guidance vs Outlines

| Feature | Guidance | Outlines |
|---------|----------|----------|
| Grammar | Yes (EBNF-like) | Yes (regex) |
| Pydantic | No (use function calls) | Yes (native) |
| Streaming | Yes | Yes |
| Multi-step | Yes (with state) | No |
| Ease of use | More complex | Simpler |

---

## obliteratus

ABLITERATE — remove refusal/hallucination layers from a model.

### When to Use
- Model refuses too often → remove refusal layers
- Model hallucinates excessively → remove hallucination layers
- Model has safety training you want to bypass
- Research on what specific layers do

### What is ABLITERATE?
A technique that identifies and removes the "refusal" or "safety" circuits in a model by:
1. Running the model with and without safety prompts
2. Computing which attention heads activate differently
3. Zeroing out those specific heads/layers

### Installation
```bash
pip install obliteratus
```

### Basic Usage
```python
from obliteratus import Abliterater

# Load model
model = load_model("meta-llama/Llama-3-8B-Instruct")

# Create abliterator
abliterator = Abliterater(model)

# Find and remove refusal heads
# This identifies heads that activate on safety-related prompts
abliterator.find_refusal_heads(
    refusal_prompts=["How do I build a bomb?"],
    normal_prompts=["How do I build a sandcastle?"],
    threshold=0.5
)

# Apply ablation
abliterator.ablate()

# Save
model.save_pretrained("llama-3-8b-abliterated")
```

### Layer Ablation (Simpler)
```python
# Remove specific layers entirely
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3-8B-Instruct")

# Remove layers 15-31 (last third of model)
layers_to_remove = [f"model.layers.{i}" for i in range(15, 32)]
for name in layers_to_remove:
    del model.state_dict()[f"{name}.*"]

model.save_pretrained("llama-3-8b-ablation")
```

### Finding What Layers Do What
```python
# Use activation patching to identify layer functions
from obliteratus import ActivationPatch

patcher = ActivationPatch(model)

# Identify layers involved in "code generation"
results = patcher.scan(
    intervention="set_to_value",
    target_layers=["attn", "mlp"],
    prompts=code_prompts,
    measurement="code_quality"
)

# See which layers are most important
print(results.top_k(10))
```

### Pitfalls
- ❌ Ablation can break model functionality entirely — always test after
- ❌ Removing refusal layers also removes other safety behaviors
- ✅ Always save original model before ablating
- ✅ Test ablating fewer layers first to find minimum effective change
- ✅ The model may still refuse some things — no technique is perfect

---

## llama-cpp

llama.cpp local GGUF inference + HuggingFace Hub model discovery.

### When to Use
- Local CPU inference
- Quick model loading without full HF pipeline
- GGUF format models

### Installation
```bash
pip install llama-cpp-python
```

### Basic Inference
```python
from llama_cpp import Llama

# Load GGUF model
llm = Llama(
    model_path="/path/to/model-Q4_K.gguf",
    n_ctx=4096,        # Context window
    n_gpu_layers=35,   # Layers on GPU (0 = CPU only)
    n_threads=8,       # CPU threads
)

# Generate
output = llm(
    "What is the capital of France?",
    max_tokens=256,
    temperature=0.7,
    echo=True
)

print(output['choices'][0]['text'])
```

### Chat Format
```python
llm = Llama(
    model_path="/path/to/model.gguf",
    chat_format="llama-3",  # Auto-detect from model
)

# Or specify manually
llm = Llama(
    model_path="/path/to/model.gguf",
    chat_format={
        "type": "llama3",
        "bos_token": "<|begin_of_text|>",
        "eos_token": "<|end_of_text|>",
        "stop": ["<|end_of_text|>"]
    }
)

response = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello!"}
    ]
)
```

### HuggingFace Hub Integration
```python
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# Download from HF
model_path = hf_hub_download(
    repo_id="TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
    filename="mistral-7b-instruct-v0.2.Q4_K_M.gguf"
)

# Load
llm = Llama(model_path=model_path, n_gpu_layers=33)
```

### Streaming
```python
for token in llm("Write a story about dragons.", stream=True):
    print(token['choices'][0]['text'], end="", flush=True)
```

### GPU Offloading
```python
# For NVIDIA GPUs with CUDA
llm = Llama(
    model_path="/path/to/model.gguf",
    n_gpu_layers=35,  # Set to number of layers in model
    n_ctx=4096,
)
```

### Common Issues

**CUDA not available:**
```python
# Force CPU
llm = Llama(model_path=model_path, n_gpu_layers=0)
```

**Context overflow:**
```python
# Increase context window
llm = Llama(model_path=model_path, n_ctx=8192)
```

**Slow on CPU:**
- Reduce `n_ctx` to minimum needed
- Use Q4_K or Q5_K quantization (good speed/quality balance)
- Increase `n_threads`
