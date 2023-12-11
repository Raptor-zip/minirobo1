import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb=512'

tokenizer = AutoTokenizer.from_pretrained("rinna/japanese-gpt-1b", use_fast=False)
model = AutoModelForCausalLM.from_pretrained("rinna/japanese-gpt-1b")

if torch.cuda.is_available():
    model = model.to("cuda")

text = "西田幾多郎は、"
token_ids = tokenizer.encode(text, add_special_tokens=False, return_tensors="pt")

with torch.no_grad():
    output_ids = model.generate(
        token_ids.to(model.device),
        max_length=100,
        min_length=100,
        do_sample=True,
        top_k=500,
        top_p=0.95,
        pad_token_id=tokenizer.pad_token_id,
        bos_token_id=tokenizer.bos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        bad_words_ids=[[tokenizer.unk_token_id]]
    )

output = tokenizer.decode(output_ids.tolist()[0])
print(output)
# sample output: 西田幾多郎は、その主著の「善の研究」などで、人間の内面に自然とその根源があると指摘し、その根源的な性格は、この西田哲学を象徴しているとして、カントの「純粋理性批判」と「判断力批判」を対比して捉えます。それは、「人が理性的存在であるかぎりにおいて、人はその当人に固有な道徳的に自覚された善悪の基準を持っている」とするもので、この理性的な善悪の観念を否定するのがカントの


# import torch
# from transformers import AutoModelForCausalLM, AutoTokenizer

# B_INST, E_INST = "[INST]", "[/INST]"
# B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
# DEFAULT_SYSTEM_PROMPT = "あなたは誠実で優秀な日本人のアシスタントです。"
# text = "竪山君という高専1年生の学生は体重が77kgもありました。そこからあらゆる困難を乗り越えて、ダイエット似成功するというプロットの短編小説を書いてください。"

# print("test")

# model_name = "elyza/ELYZA-japanese-Llama-2-7b-instruct"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)

# if torch.cuda.is_available():
#     print("OK")
#     model = model.to("cuda")

# print(19)

# prompt = "{bos_token}{b_inst} {system}{prompt} {e_inst} ".format(
#     bos_token=tokenizer.bos_token,
#     b_inst=B_INST,
#     system=f"{B_SYS}{DEFAULT_SYSTEM_PROMPT}{E_SYS}",
#     prompt=text,
#     e_inst=E_INST,
# )


# with torch.no_grad():
#     token_ids = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")

#     output_ids = model.generate(
#         token_ids.to(model.device),
#         max_new_tokens=256,
#         pad_token_id=tokenizer.pad_token_id,
#         eos_token_id=tokenizer.eos_token_id,
#     )
# output = tokenizer.decode(output_ids.tolist()[0][token_ids.size(1) :], skip_special_tokens=True)
# print(output)