import json
path = 'PATH--TO--RESULT OF MODEL'

with open(path, 'r') as f:
    data = [json.loads(line) for line in f]

hallu_map = {
    '0': 'Catastrophic Hallucinations', #  0
    '1': 'Critical Hallucinations', # 0.2
    '2': 'Attribute Hallucinations', # 0.4
    '4': 'Minor Hallucinations', # 0.8
    '5': 'Correct Statements' # 1
}

correct = 0

miss = 0
miss_save = []

ok_score = {} 


for item in data:
    id = str(item['report_id'])
    if id not in ok_score:
        ok_score[id] = [0, 0]
        
    text = item['text']
    text = text.lower()
    
    if 'catastrophic' in text:
        ok_score[id][1] += 1
        
    elif 'critical' in text:
        ok_score[id][1] += 1
        ok_score[id][0] += 0.2
        
    elif 'attribute' in text:
        ok_score[id][1] += 1
        ok_score[id][0] += 0.4
    
    ####   
    elif 'minor' in text and 'correct' in text and 'AttrGPT' in path:
        ok_score[id][1] += 1
        ok_score[id][0] += 1
        
    elif 'minor' in text:
        ok_score[id][1] += 1
        ok_score[id][0] += 0.8
    
    elif 'correct' in text or 'no hallucination' in text:
        ok_score[id][1] += 1
        ok_score[id][0] += 1
        correct += 1
        
    elif 'AttrGPT' in path:
        ok_score[id][1] += 1
        ok_score[id][0] += 0.4
        correct += 1
        miss += 1
        miss_save.append(item)
        
    else:
        ok_score[id][1] += 1
        ok_score[id][0] += 0
        miss += 1
        miss_save.append(item)


print(miss_save)
print("miss: ", miss)
print('***************************************************')
print('***************************************************')

total_score = 0
total_nums = len(ok_score)

for k, v in ok_score.items():
    curr_score = v[0]
    curr_nums = v[1]
    curr_ave = curr_score / curr_nums
    total_score += curr_ave

total_sen_nums = len(data)

print('total_nums: ', total_nums)
print("total_score: ", total_score)
print("Medihall_score: ", total_score / total_nums)
print("ACC: ", correct / total_sen_nums)

log_path = path.replace('hall_result.jsonl', 'metric_log.txt')
with open(log_path, 'w') as f:
    f.write(f'total_nums: {total_nums}' + '\n')
    f.write(f'total_score: {total_score}' + '\n')
    f.write(f'Medihall_score: {(total_score / total_nums)}' + '\n')
    f.write(f'ACC: {(correct / total_sen_nums)}' + '\n')
