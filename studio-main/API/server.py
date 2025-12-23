from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from ultralytics import YOLO
from PIL import Image
import logging
import json
import io
import os
import uvicorn

# FastAPI 앱 초기화
app = FastAPI(
    title="Medicine Object Detection API",
    description="YOLO 모델을 사용하여 의약품 객체를 탐지하는 API입니다.",
    version="1.0.0"
)

# Logging 설정: 콘솔 출력 + 파일 저장
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "predictions.log")
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("medicine_api")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(sh)
    logger.addHandler(fh)

# 모델 경로 설정 (절대 경로로 설정하여 오류 방지)
# 프로젝트 루트: /Users/apple/Downloads/_Part_2/Project
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "models", "best.pt")

# 모델 전역 변수
model = None

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 모델을 로드합니다."""
    global model
    if os.path.exists(MODEL_PATH):
        print(f"Loading model from {MODEL_PATH}")
        model = YOLO(MODEL_PATH)
    else:
        print(f"Model not found at {MODEL_PATH}")
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

@app.get("/")
async def root():
    return {"message": "Medicine Object Detection API is running"}

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    """
    이미지 파일을 업로드받아 객체 탐지를 수행합니다.
    """
    global model
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    # 이미지 유효성 검사
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # 이미지 읽기
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # 추론 수행
        results = model(image)
        
        # 결과 처리
        predictions = []
        for result in results:
            # Boxes 객체 추출
            for box in result.boxes:
                # 좌표, 신뢰도, 클래스 추출
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf[0])
                cls_id = int(box.cls[0])
                class_name = model.names[cls_id]
                
                predictions.append({
                    "box": [x1, y1, x2, y2],
                    "confidence": confidence,
                    "class_id": cls_id,
                    "class_name": class_name
                })
                # 간단한 콘솔 출력: 클래스명, 박스 좌표, 신뢰도
                try:
                    print(f"Prediction: {class_name} box={[x1, y1, x2, y2]} conf={confidence:.4f}")
                except Exception:
                    # print 실패는 무시
                    pass
        
        # Build `pills` response containing each detection's name and box.
        # Returns one entry per detection (preserves multiple detections of same class).
        # Format:
        # {
        #   "pills": [ { "pillName": "Ibuprofen 200mg", "box": [x1,y1,x2,y2] }, ... ]
        # }
        # Deduplicate by class_name: keep the detection with highest confidence per class.
        best_by_class = {}
        seen_order = []
        for p in predictions:
            name = p.get("class_name")
            box = p.get("box")
            conf = p.get("confidence", 0.0)
            if not name or not box:
                continue
            # record order of first appearance
            if name not in best_by_class:
                seen_order.append(name)
                best_by_class[name] = {"box": [float(b) for b in box], "confidence": float(conf)}
            else:
                # replace if this detection has higher confidence
                if float(conf) > float(best_by_class[name]["confidence"]):
                    best_by_class[name] = {"box": [float(b) for b in box], "confidence": float(conf)}

        pills = []
        for name in seen_order:
            entry = best_by_class.get(name)
            if entry:
                pills.append({"pillName": name, "box": entry["box"]})
        # Log inference result (filename + payload)
        try:
            payload = {"pills": pills}
            logger.info(f"Inference - file=%s result=%s", file.filename, json.dumps(payload, ensure_ascii=False))
        except Exception:
            logger.exception("Failed to log inference payload")

        return JSONResponse(content={"pills": pills})

    except Exception as e:
        logger.exception("Inference error for file: %s", getattr(file, "filename", "<unknown>"))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # 포트 8000번에서 실행
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
