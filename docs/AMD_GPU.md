# AMD MI300X pipeline for ProbePilot

Run training and inference on **AMD Developer Cloud** Instinct MI300X instances with ROCm.

## Recommended image packages

- ROCm-enabled PyTorch ([AMD / PyTorch install matrix](https://rocm.docs.amd.com/))
- `vllm` with ROCm backend when available for your stack
- Hugging Face `transformers`, `datasets`, `peft` (LoRA / QLoRA)
- `optimum-amd` where applicable for accelerated HF models

## Fine-tuning (QLoRA) — what to train

Do **not** memorize textbooks in the adapter. Keep facts in RAG. Fine-tune only on:

- Diagnostic reasoning style
- JSON tool calls (`multimeter`, `oscilloscope`, `switch_matrix`, `simulator`)
- Measurement planning and next-best-measure
- Fault ranking and confidence calibration
- Expected vs measured comparison narratives

## Serving

- Batch / offline eval: HF + ROCm
- Online low-latency: `vllm serve` on MI300X (pin versions to the cloud image)

## Metrics to record (template)

| Stage | Metric | Notes |
|-------|--------|--------|
| Training | Wall time | hours:minutes |
| Training | GPU memory peak | `rocm-smi` / profiler |
| Inference | p50 / p95 latency | ms per request |
| Inference | tokens/sec | decode throughput |
| Quality | Base vs FT accuracy | held-out diagnostic set |
| Product | Avg diagnosis confidence | before/after FT + RAG |

Log **base vs fine-tuned** accuracy and **confidence improvement** on a frozen diagnostic benchmark (JSON inputs with known fault labels).

## Long-context RAG + tools

Use RAG for datasheets and manuals; keep tool schemas in system prompt; stream partial JSON over WebSocket for the UI timeline.
