import subprocess
import json

def ask_ai(prompt):
    # 테스트용 (나중에 AI 연결)
    return """
import json

def predict():
    return ["A", "B"]

if __name__ == "__main__":
    print(json.dumps(predict()))
"""

def evaluate(predictions, data):
    correct = 0
    for p, d in zip(predictions, data):
        if p == d["real"]:
            correct += 1
    return correct / len(data)

# 데이터 불러오기
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

prompt = "예측 모델 만들어라"

for i in range(5):
    code = ask_ai(prompt)

    with open("predict.py", "w") as f:
        f.write(code)

    result = subprocess.run(
        ["python", "predict.py"],
        capture_output=True,
        text=True
    )

    try:
        predictions = json.loads(result.stdout)
    except:
        prompt += "\n출력 JSON 형식으로 수정해"
        continue

    acc = evaluate(predictions, data)
    print("정확도:", acc)

    if acc >= 0.5:
        print("완료")
        break

    prompt += f"\n정확도 낮음 {acc}, 개선해"