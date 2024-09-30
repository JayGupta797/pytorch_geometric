# This example shows how to top the OGBG leaderboard using GNN+LLM
# hyperparams are hardcoded
import torch
from g_retriever import train

from torch_geometric.nn.models import GAT, GRetriever
from torch_geometric.nn.nlp import LLM
from torch_geometric.datasets import OGBG_Code2


def get_loss(model, batch, **kwargs) -> torch.Tensor:
    return model(batch.question, batch.x, batch.edge_index, batch.batch,
                 batch.ptr, '|'.join(batch.label), batch.edge_attr, batch.desc)


def inference_step(model, batch, **kwargs):
    pred = model.inference(batch.question, batch.x, batch.edge_index,
                           batch.batch, batch.ptr, batch.edge_attr, batch.desc)
    eval_data = {
        "pred": pred,
        "question": batch.question,
        "desc": batch.desc,
        "label": '|'.join(batch.label)
    }
    print("using correct func")
    return eval_data


gnn_to_use = GAT(in_channels=1024, hidden_channels=1024, out_channels=1024,
                 num_layers=4, heads=4)
llm_to_use = LLM(model_name="meta-llama/CodeLlama-7b-Python-hf", num_params=7)
# This would require a data center scale hardware setup
# llm_to_use = LLM(model_name="deepseek-ai/DeepSeek-Coder-V2-Base",
#                  num_params=236)
CodeRetriever = GRetriever(
    llm=llm_to_use,
    gnn=gnn_to_use,
)

train(num_epochs=5, hidden_channels=None,
    num_gnn_layers=None, batch_size=16, eval_batch_size=32,
    lr=1e-5, checkpointing=True, model=CodeRetriever,
    dataset=OGBG_Code2)
torch.cuda.empty_cache()
torch.cuda.reset_max_memory_allocated()
gc.collect()
