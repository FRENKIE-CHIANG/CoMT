import json
from bert_score import score
from transformers import AutoTokenizer
from nltk.translate.meteor_score import meteor_score
from rouge import Rouge
import sacrebleu
import pandas as pd

file_path = r'PATH--TO--RESULT OF MODEL'

model_base = r'PATH--TO--MODEL'
tokenizer = AutoTokenizer.from_pretrained(model_base, use_fast=False)

def read_jsol_file(file_path):
    med_vlm_answers = []
    ground_truths = []


    with open(file_path, 'r') as file:
        data_list = json.load(file)
        for data in data_list:
            
            # Use 'or' to handle different possible keys
            med_vlm_answer = data.get("text") or data.get("answer")
            
            words = med_vlm_answer.split()
            truncated_words = words[:20]
            med_vlm_answer = ' '.join(truncated_words)
            
            
            ground_truth = data.get("ground_truth") or data.get("ground-truth")
               
            if med_vlm_answer is not None:
                text = med_vlm_answer.strip("### Assistant: ")
                text = text.rstrip('</s>')
                if '\n#' in text:
                    parts = text.split('\n#')
                    text = parts[0]
                    text = text.strip()
                med_vlm_answers.append(text)
            if ground_truth is not None:
                ground_truths.append(ground_truth)
    return med_vlm_answers, ground_truths

def calculate_average_bertscore(cands, refs):
    P, R, F1 = score(cands=cands, refs=refs, lang="en", verbose=True)
    return P.mean().item(), R.mean().item(), F1.mean().item()

med_vlm_answers, ground_truths = read_jsol_file(file_path)

average_P, average_R, average_F1 = calculate_average_bertscore(med_vlm_answers, ground_truths)
# print(f"Average BERTScore Precision: {average_P}")
# print(f"Average BERTScore Recall: {average_R}")
print(f"Average BERTScore F1: {average_F1}")

def calculate_average_meteor_score(cands, refs, tokenizer):
    total_score = 0
    for cand, ref in zip(cands, refs):
        hypothesis_tokens = tokenizer.tokenize(cand)
        reference_tokens = tokenizer.tokenize(ref)
        score = meteor_score([reference_tokens], hypothesis_tokens)
        total_score += score
    return total_score / len(cands) if cands else 0

def calculate_average_rouge_scores(cands, refs):
    rouge = Rouge()
    total_recall_1, total_precision_1, total_f1_1 = 0, 0, 0
    total_recall_2, total_precision_2, total_f1_2 = 0, 0, 0
    total_recall_l, total_precision_l, total_f1_l = 0, 0, 0
    valid_count_1 = valid_count_2 = valid_count_l = 0

    for cand, ref in zip(cands, refs):
        if not cand.strip():
            print(f"Empty candidate: '{cand}', ground truth: '{ref}'")
            valid_count_1 += 1
            valid_count_2 += 1
            valid_count_l += 1
        else:
            scores = rouge.get_scores(cand, ref)
            total_recall_1 += scores[0]['rouge-1']['r']
            total_precision_1 += scores[0]['rouge-1']['p']
            total_f1_1 += scores[0]['rouge-1']['f']
            valid_count_1 += 1
            
            total_recall_2 += scores[0]['rouge-2']['r']
            total_precision_2 += scores[0]['rouge-2']['p']
            total_f1_2 += scores[0]['rouge-2']['f']
            valid_count_2 += 1
            
            total_recall_l += scores[0]['rouge-l']['r']
            total_precision_l += scores[0]['rouge-l']['p']
            total_f1_l += scores[0]['rouge-l']['f']
            valid_count_l += 1

    average_recall_1 = total_recall_1 / valid_count_1 if valid_count_1 else 0
    average_precision_1 = total_precision_1 / valid_count_1 if valid_count_1 else 0
    average_f1_1 = total_f1_1 / valid_count_1 if valid_count_1 else 0

    average_recall_2 = total_recall_2 / valid_count_2 if valid_count_2 else 0
    average_precision_2 = total_precision_2 / valid_count_2 if valid_count_2 else 0
    average_f1_2 = total_f1_2 / valid_count_2 if valid_count_2 else 0

    average_recall_l = total_recall_l / valid_count_l if valid_count_l else 0
    average_precision_l = total_precision_l / valid_count_l if valid_count_l else 0
    average_f1_l = total_f1_l / valid_count_l if valid_count_l else 0

    return (average_recall_1, average_precision_1, average_f1_1,
            average_recall_2, average_precision_2, average_f1_2,
            average_recall_l, average_precision_l, average_f1_l)


average_meteor = calculate_average_meteor_score(med_vlm_answers, ground_truths, tokenizer)
print(f"Average METEOR Score: {average_meteor}")

(average_recall_1, average_precision_1, average_f1_1,
 average_recall_2, average_precision_2, average_f1_2,
 average_recall_l, average_precision_l, average_f1_l) = calculate_average_rouge_scores(med_vlm_answers, ground_truths)

print(f"Average ROUGE-1 Recall: {average_recall_1}")
print(f"Average ROUGE-1 Precision: {average_precision_1}")
print(f"Average ROUGE-1 F1 Score: {average_f1_1}")

print(f"Average ROUGE-2 Recall: {average_recall_2}")
print(f"Average ROUGE-2 Precision: {average_precision_2}")
print(f"Average ROUGE-2 F1 Score: {average_f1_2}")

print(f"Average ROUGE-L Recall: {average_recall_l}")
print(f"Average ROUGE-L Precision: {average_precision_l}")
print(f"Average ROUGE-L F1 Score: {average_f1_l}")

def calculate_average_token_length(cands, tokenizer):
    total_length = 0
    
    for cand in cands:
        tokens = tokenizer.tokenize(cand)
        total_length += len(tokens)
    
    average_length = total_length / len(cands) if cands else 0
    return average_length

average_token_length = calculate_average_token_length(med_vlm_answers, tokenizer)
print(f"Average Token Length of Med-VLM Answers: {average_token_length}")

def calculate_bleu(cands, refs):
    bleu = sacrebleu.corpus_bleu(cands, [refs])
    return bleu.score

# 计算并打印BLEU得分
average_bleu = calculate_bleu(med_vlm_answers, ground_truths)
print(f"Average BLEU Score: {average_bleu}")


# 保存结果到JSON文件
results = {
    "File Path": file_path,
    "Average BERTScore Precision": average_P,
    "Average BERTScore Recall": average_R,
    "Average BERTScore F1": average_F1,
    "Average METEOR Score": average_meteor,
    "Average ROUGE-1 Recall": average_recall_1,
    "Average ROUGE-1 Precision": average_precision_1,
    "Average ROUGE-1 F1 Score": average_f1_1,
    "Average ROUGE-2 Recall": average_recall_2,
    "Average ROUGE-2 Precision": average_precision_2,
    "Average ROUGE-2 F1 Score": average_f1_2,
    "Average ROUGE-L Recall": average_recall_l,
    "Average ROUGE-L Precision": average_precision_l,
    "Average ROUGE-L F1 Score": average_f1_l,
    "Average Token Length of Med-VLM Answers": average_token_length,
    "Average BLEU Score": average_bleu
}

outout_path = r'PATH--TO--SAVE'
with open(outout_path, 'w') as json_file:
    json.dump(results, json_file, indent=4)

with open(outout_path, 'r') as json_file:
    data = json.load(json_file)
    df = pd.DataFrame(data, index=[0])

# csv_output_path = r'/Dataset3/jy_data/EM24/EVAL/hallu_eval/word_metric_log/evaluation_results.csv'
# df.to_csv(csv_output_path, index=False)

# print(df)