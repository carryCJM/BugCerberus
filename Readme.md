<p align="center">
    <img src="./fig/cerberus.png" alt="BugCerberus Logo" width="100">
</p>

# Bridging Bug Localization and Issue Fixing: A Hierarchical Localization Framework Leveraging Large Language Models

To enhance the precision of issue fixing by accurately identifying bug locations in large-scale projects, this project presents **BugCerberus**, the first hierarchical bug localization framework powered by three customized large language models (LLMs). 

- **BugCerberus** analyzes intermediate representations of bug-related programs at **file, function, and statement levels**, extracting bug-related contextual information from these representations.
- At each level, **BugCerberus** employs customized LLMs trained using bug reports and code contexts to learn bug patterns.
- Finally, BugCerberus hierarchically searches for bug-related code elements across all three levels, using the well-tuned models to localize bugs.

With BugCerberus, we further investigate the impact of bug localization precision on the effectiveness of issue fixing.

---

## Project Structure


### Directory Explanation

- **data**  
    Contains model checkpoints, repair results, and training data samples used in BugCerberus.


- **src**  
    Contains the source code for model training, including scripts for fine-tuning 
**BugCerberus** using LLaMA models.

- **Static Analysis**  
    Provides scripts for extracting code context at three granularity levels: **file-level**, **function-level**, and **statement-level**.

---

## Usage Instructions

### 1. Install Dependencies
Before running the training process, install the required dependencies using:

```bash
pip install -r requirements.txt
```
### 2. Fine-tuning BugCerberus
Navigate to the src directory and run the following command to fine-tune the BugCerberus model using LlamaFactory:
```bash
llamafactory-cli train \
    --stage sft \
    --do_train \
    --model_name_or_path modelPath \
    --dataset trainDataSet \
    --dataset_dir ./data \
    --template llama3 \
    --finetuning_type lora \
    --output_dir output_dir \
    --overwrite_cache \
    --overwrite_output_dir \
    --cutoff_len 1024 \
    --preprocessing_num_workers 16 \
    --per_device_train_batch_size 10 \
    --per_device_eval_batch_size 4 \
    --gradient_accumulation_steps 8 \
    --lr_scheduler_type cosine \
    --logging_steps 500 \
    --warmup_steps 750 \
    --save_steps 1500 \
    --eval_steps 1500 \
    --evaluation_strategy steps \
    --load_best_model_at_end \
    --learning_rate 5e-5 \
    --num_train_epochs 3.0 \
    --val_size 0.1 \
    --plot_loss \
    --fp16
```
##Acknowledgments
arts of the code are adapted from [Joern](https://github.com/joernio/joern) and [LlamaFactory](https://github.com/hiyouga/LLaMA-Factory).
