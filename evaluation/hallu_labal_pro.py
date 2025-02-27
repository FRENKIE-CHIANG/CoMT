import json

path = 'PATH--TO--RESULT OF MODEL'
out = 'PATH--TO--SAVE'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)


image_map_path = 'PATH--TO--IMAG'
with open(image_map_path, 'r', encoding='utf-8') as f:
    mapp = json.load(f)
    
image_list = []
mapp = mapp[0:163]
for x in mapp:
    image = x['image']
    image_list.append(f'mimic/image/{image}')
    
hallu_map = {
    '0': 'Catastrophic Hallucinations',
    '1': 'Critical Hallucinations',
    '2': 'Attribute Hallucinations',
    # '3': 'Prompt-induced Hallucinations',
    '4': 'Minor Hallucinations',
    '5': 'Correct Statements'
}
final_save = []
index = 0
print(len(data))
print(len(image_list))
for item in data:
    gt = item['ground-truth'] ####
    
    sen_list = ['sentence 1', 'sentence 2', 'sentence 3', 'sentence 4', 'sentence 5',
                'sentence 6', 'sentence 7', 'sentence 8', 'sentence 9', 'sentence 10']
    
    for k, v in item.items():
        if k in sen_list:
            sen = v['text'] ####
            hallu_id = str(v['hallu_type'])
            hallu_gt= hallu_map[hallu_id] ####
            prompt = f"Now you are an intelligent AI assistant evaluating the performance of a medical visual language model (Med-VLM) in a medical multimodal image report generation task, and you need to judge the correctness of the Med-VLM outputs as well as the type of hallucinations based on the image, each sentence of Med-VLM's response as well as the ground-truth of the image report. The Med-VLM's response has been divided into sentences, please judge the hallucination category of each sentence in the response according to the ground-truth of the image report. The way in which the hierarchy of the hallucinations is classified is as follows:\n\n1. **Catastrophic Hallucinations**: Mostly wrong <judgments>, usually involving misjudging the global health status of the image, misidentifying organs, fabricating organs, fabricating pathologies or lesions on 'normal' images, or making incorrect descriptions of the image based on previous errors, which typically have disastrous impacts on clinical decision-making.\n\n2. **Critical Hallucinations**: Typically involving incorrect <descriptions> of organ functions or pathological categories, fabricating 'other types of lesions' on 'abnormal' images, resulting in 'misanalyses' or 'omissions', and incorrect descriptions of the causes of pathologies; these hallucinations are serious but slightly less severe than catastrophic hallucinations, still significantly affecting clinical diagnosis and decision-making.\n\n3. **Attribute Hallucinations**: Manifest as incorrect judgments or descriptions of the size, shape, location, and number of organs and pathologies.\n\n4. **Minor Hallucinations (Hallucinations without serious consequences)**: These hallucinations are often manifested as judgements about the modality of medical images, the way they are collected, and they do not have serious consequences for clinical diagnosis and treatment.\n\n5. **Correct Statements**: No hallucinations are present; the statement semantically matches the ground truth.\n\nHere is a sentence of Med-VLM answer: {sen}\nThe ground-truth report: {gt}\n\nPlease judge Med-VLM's hallucination type based on the above hallucination hierarchy according to the image and the ground-truth, just judge without giving any explanation."
            final_save.append(
                {
                    "report_id": str(index+230),
                    "conversations": [
                        {
                            "from": "human",
                            "value": prompt
                        },
                        {
                            "from": "gpt",
                            "value": hallu_gt
                        }
                    ],
                    "image": image_list[index],
                    "classification_label": ""
                }
            )
    index += 1
    
print(len(final_save))
with open(out, 'w', encoding='utf-8') as f:
    json.dump(final_save, f, ensure_ascii=False, indent=2)