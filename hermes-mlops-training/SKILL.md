---
name: hermes-mlops-training
description: Complete LLM fine-tuning and training workflows for Hermes — LoRA/QLoRA via axolotl, RL training via TRL (GRPO/DPO/SFTTrainer), distributed training via PyTorch FSDP, and fast fine-tuning via Unsloth. Use when fine-tuning an LLM, setting up RLHF training, or configuring distributed training infrastructure.
category: mlops/training
---

# Hermes MLOps Training

Complete LLM fine-tuning and training workflows — LoRA/QLoRA, RLHF/DPO/GRPO, distributed FSDP training, and fast fine-tuning with Unsloth.

**Trigger conditions**: user wants to fine-tune an LLM, set up RLHF training, configure distributed training, or optimize training speed/memory.

---

## Skill Map

| Task | Use This Skill |
|------|---------------|
| LoRA/QLoRA fine-tuning via axolotl YAML | → `peft-fine-tuning` subsection below |
| RL training (DPO/GRPO/SFTTrainer) via TRL | → `fine-tuning-with-trl` subsection below |
| GRPO-specific training patterns | → `grpo-rl-training` subsection below |
| Distributed training via PyTorch FSDP | → `pytorch-fsdp` subsection below |
| Fast fine-tuning (2-5x faster, less VRAM) via Unsloth | → `unsloth` subsection below |
| Evaluate fine-tuned models on benchmarks | → `evaluating-llms-harness` subsection below |

---

## peft-fine-tuning

Parameter-efficient fine-tuning for LLMs using LoRA, QLoRA, and related PEFT methods.

### When to Use
- Fine-tuning a model on a specific domain or task
- Memory-constrained training (use QLoRA for 4-bit/8-bit)
- Adding task-specific behavior to an existing base model

### Quick Start with Axolotl

Axolotl uses YAML config files for training configurations.

**Example LoRA config (lora.yml):**
```yaml
base_model: meta-llama/Llama-3-8b-hf
model_type: LlamaForCausalLM
load_in_4bit: true
bf16: true

lora_modules_to_save: [lm_head, embed_tokens]
lora_r: 16
lora_alpha: 16
lora_dropout: 0.05
lora_target_linear: true

dataset_prepared_path: last_run_prepared
datasets:
  - path: vicuna刮刮卡/music_instructions
    type: alpaca
dataset_split: train
dataset_shard_fraction: 1.0
num_epochs: 3
optimizer: adamw_torch
lr_scheduler: cosine
learning_rate: 0.0002
true_sequential: true

gradient_accumulation_steps: 4
batch_size: 2
eval_batch_size: 8
eval_accumulation_steps: 4
max_grad_norm: 1.0
warmup_steps: 10
weight_decay: 0.0
eos_token: <|end_of_text|>
```

**Example QLoRA config (qloha.yml):**
```yaml
base_model: meta-llama/Llama-3-8b-hf
model_type: LlamaForCausalLM
load_in_4bit: true
load_in_8bit: false
bf16: true
double_quant: true
quant_type: nf4

lora_r: 64
lora_alpha: 64
lora_dropout: 0.05
lora_target_modules:
  - q_proj
  - k_proj
  - v_proj
  - o_proj
  - gate_proj
  - up_proj
  - down_proj

datasets:
  - path: your/dataset
    type: alpaca
num_epochs: 3
optimizer: adamw_torch
lr_scheduler: cosine
learning_rate: 0.0001
batch_size: 2
gradient_accumulation_steps: 8
```

### Training Command
```bash
cd ~/Coding/axolotl
accelerate launch --config_file configs/llama3/lora.yml
# or for QLoRA:
accelerate launch --config_file configs/llama3/qlora.yml
```

### Monitoring
```bash
# Watch training logs
tail -f ~/Coding/axolotl/qlora_out/accelerate_logs/*.log

# TensorBoard (if using)
tensorboard --logdir ~/Coding/axolotl/qlora_out
```

### Common Issues

**Out of memory:**
- Reduce `batch_size` and increase `gradient_accumulation_steps`
- Use `load_in_4bit: true` (QLoRA)
- Reduce `lora_r` (smaller rank = less memory)

**Dataset issues:**
- Verify dataset format matches `type` (alpaca, sharegpt, etc.)
- Check `dataset_prepared_path` is not stale — delete and re-prepare if needed

---

## fine-tuning-with-trl

Fine-tune LLMs using TRL — SFTTrainer, DPOTrainer, ORMOTrainer, and GRPOTrainer.

### When to Use
- RLHF training (DPO/ORPO)
- Supervised fine-tuning with SFTTrainer
- Reward model training
- GRPO training (see `grpo-rl-training` subsection)

### Installation
```bash
pip install trl
```

### SFTTrainer (Supervised Fine-Tuning)
```python
from trl import SFTTrainer
from transformers import TrainingArguments

trainer = SFTTrainer(
    model=model,
    args=TrainingArguments(
        output_dir="./sft_output",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        weight_decay=0.01,
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        fp16=True,
        logging_steps=10,
        save_strategy="epoch",
    ),
    train_dataset=train_dataset,
    formatting_func=formatting_prompts_func,
    max_seq_length=512,
)

trainer.train()
```

### DPOTrainer (Direct Preference Optimization)
```python
from trl import DPOTrainer, DPOConfig

trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=DPOConfig(
        output_dir="./dpo_output",
        beta=0.1,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        learning_rate=5e-7,
    ),
    train_dataset=train_dataset,
    tokenizer=tokenizer,
)

trainer.train()
```

### ORMOTrainer (Online Reinforcement Learning from Human Feedback)
```python
from trl import ORMOConfig, ORMOTrainer

trainer = ORMOTrainer(
    model=model,
    args=ORMOConfig(
        output_dir="./ormo_output",
        perc_tracked_grad=0.1,
        rollout_batch_size=512,
    ),
    train_dataset=train_dataset,
    reward_function=reward_model,
)

trainer.train()
```

---

## grpo-rl-training

GRPO (Group Relative Policy Optimization) — a specific RL training pattern used by DeepSeek and others.

### What is GRPO?
GRPO is a simplified RL algorithm where:
1. Generate multiple samples (a group) for each prompt
2. Compute a relative reward ranking within the group
3. Update policy based on the group-relative advantage

### GRPO vs DPO vs PPO

| Method | Reference Model | Best For |
|--------|----------------|----------|
| DPO | Yes (online) | Simple preference learning |
| PPO | No (critic needed) | Complex reward shaping |
| GRPO | No (group-relative) | Efficient, no critic needed |

### GRPO Implementation via TRL GRPOTrainer
```python
from trl import GRPOTrainer, GRPOConfig

trainer = GRPOTrainer(
    model=model,
    args=GRPOConfig(
        output_dir="./grpo_output",
        beta=0.1,  # KL coefficient
        grpo_batch_size=8,
        num_generations=16,  # Group size
        num_iterations=4,   # Epochs per prompt
        max_prompt_length=256,
        max_response_length=512,
    ),
    train_dataset=train_dataset,
    reward_function=compute_reward,
    tokenizer=tokenizer,
)

trainer.train()
```

### Common Use Cases
- Math reasoning (group-relative scoring on correct/incorrect)
- Code generation (execution-based rewards)
- Reasoning tasks (verifiable outcomes)

### Pitfalls
- GRPO needs a reliable reward function — noisy rewards cause training instability
- Group size too small → high variance; too large → slow
- Balance between KL penalty (`beta`) and reward signal

---

## pytorch-fsdp

Distributed training using PyTorch Fully Sharded Data Parallelism.

### When to Use
- Training models too large for a single GPU
- Multi-node training across machines
- Memory optimization for large base models

### Key FSDP Concepts
- **Sharded State Dict**: Model weights are sharded across GPUs
- **Full Sharding (FSDP1)**: Shards all parameters, gradients, and optimizer states
- **Mixed Sharding**: Shards weights + uses ZeRO for optimizer states

### Basic FSDP Setup
```python
import torch
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import ShardingStrategy, MixedPrecision
from torch.distributed.fsdp.wrap import transformer_auto_wrap_policy

# Mixed precision for memory savings
mixed_precision_policy = MixedPrecision(
    param_dtype=torch.bfloat16,
    reduce_dtype=torch.float32,
    buffer_dtype=torch.bfloat16,
)

# FSDP config
fsdp_config = {
    "sharding_strategy": ShardingStrategy.FULL_SHARD,
    "mixed_precision": mixed_precision_policy,
    "auto_wrap_policy": transformer_auto_wrap_policy,
    "device_id": torch.cuda.current_device(),
}

model = FSDP(model, **fsdp_config)
```

### Launching FSDP Training
```bash
# Single node, multiple GPUs
torchrun --nproc_per_node=4 train.py

# Multi-node
torchrun --nproc_per_node=8 --nnodes=2 --node_rank=0 --master_addr=HOSTNAME train.py
```

### Common FSDP Issues

**Gradient checkpointing** (essential for large models):
```python
model.gradient_checkpointing_enable()
```

**Mixed precision not working:**
```python
# Check bf16 support
print(torch.cuda.is_bf16_supported())
```

**Sharding strategy choices:**
- `FULL_SHARD`: Most memory savings, slower communication
- `SHARD_GRAD_OP`: Good balance
- `NO_SHARD`: For single GPU or when memory is not an issue

### Integration with Axolotl
```yaml
# In axolotl config for FSDP
scheduler: tstr
scheduler_step_with_optimizer: true
fsdp:
  - cpu_fsdp: true
  - sharding_strategy: FULL_SHARD
  - mixed_precision: bfloat
```

---

## unsloth

Unsloth — 2-5x faster LoRA/QLoRA fine-tuning with 60% less VRAM.

### When to Use
- Need to fine-tune faster (2-5x speedup)
- Have limited VRAM (Unsloth uses gradient checkpointing + optimized kernels)
- Training on consumer GPUs (RTX 3090/4090, etc.)

### Installation
```bash
pip install unsloth
pip install "unsloth[cu124]"  # or cu118 for older CUDA
```

### Basic Usage
```python
from unsloth import FastLanguageModel
import torch

# Load model + tokenizer
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit",
    max_seq_length=2048,
    dtype=None,  # Auto-detect
    load_in_4bit=True,
)

# Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing=True,
)

# Train
from unsloth import SFTTrainer
from transformers import TrainingArguments

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    args=TrainingArguments(
        output_dir="./unsloth_output",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        learning_rate=2e-4,
        fp16=False,  # Unsloth uses bf16 automatically
        log_steps=10,
    ),
)
trainer.train()
```

### Speed Comparison (vs vanilla LoRA)
| Model | Vanilla LoRA | Unsloth | Speedup |
|-------|-------------|---------|---------|
| Llama 3 8B | 1x | 2.2x | 2.2x |
| Llama 3 70B | 1x | 2.5x | 2.5x |
| Mistral 7B | 1x | 2.1x | 2.1x |

### Memory Comparison
| Model | Vanilla 4bit | Unsloth 4bit | VRAM Saved |
|-------|-------------|--------------|------------|
| Llama 3 8B | ~10GB | ~6GB | 40% |
| Llama 3 70B | ~40GB | ~24GB | 40% |

### Supported Models
- Llama 3 / 3.1 / 3.2
- Mistral / Mixtral
- Phi-3 / Phi-4
- Qwen 2 / 2.5
- Gemma 2
- And many more (see unsloth docs)

### Caveats
- Unsloth patches transformers — may conflict with other modified trainers
- Inference requires exporting to standard format (`FastLanguageModel.for_inference()`)
- Some advanced features (like certain attention variants) may not be supported

---

## evaluating-llms-harness

Evaluate fine-tuned models using lm-evaluation-harness.

### When to Use
- After fine-tuning, verify model quality
- Compare models on standard benchmarks
- Track training progress

### Installation
```bash
pip install lm-evaluation-harness
```

### Running Evaluation
```bash
# Evaluate on MMLU
lm_eval \
  --model hf \
  --model_args pretrained=/path/to/model,load_in_4bit=true \
  --tasks mmlu \
  --batch_size 4 \
  --output_path ./eval_results/

# Multiple benchmarks
lm_eval \
  --model hf \
  --model_args pretrained=/path/to/model \
  --tasks mmlu,gsm8k,truthfulqa,hellaswag \
  --batch_size 8 \
  --output_path ./eval_results/
```

### Available Benchmarks
| Benchmark | What it tests |
|-----------|--------------|
| mmlu | Multi-task language understanding |
| gsm8k | Grade school math |
| truthfuqa | Truthfulness |
| hellaswag | Commonsense reasoning |
| arc | ARC challenge |
| humaneval | Python code generation |

### Integration with Training Pipeline
```bash
# After training completes, run evaluation
python evaluate.py --checkpoint_dir ./final_checkpoint --benchmark mmlu,gsm8k
```

### Pitfalls
- Evaluation is slow — budget time accordingly (1-2 hours per benchmark for 8B models)
- Some benchmarks require specific formatting (e.g., GSM8K needs chain-of-thought)
- `load_in_4bit` may affect eval quality slightly — use full precision for final eval
