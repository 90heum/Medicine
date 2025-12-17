from ultralytics import YOLO
import os
import torch

class Predictor:
    """
    config.yaml 기반으로 YOLO 모델 추론을 수행하는 클래스입니다.

    이 클래스는 학습이 완료된 YOLO 모델을 로드하여,
    지정된 이미지 디렉토리 내의 모든 이미지에 대해
    객체 탐지 추론을 일괄 수행합니다.

    핵심 특징:
        - config(dict) 기반 추론 설정 관리
        - GPU 사용 가능 시 자동으로 CUDA 사용
        - CategoryMapper를 통한 YOLO → COCO category_id 복원
        - 추론 결과를 구조화된 dict 형태로 반환

    사용 목적:
        - 대회 제출용 결과 생성
        - 후처리(CSV 변환, 시각화 등)의 입력 데이터 생성
        - 배치 단위 추론 파이프라인 구성
    """

    def __init__(self, config: dict, mapper):
        """
        Predictor 객체를 초기화합니다.

        설정 파일(config)과 CategoryMapper를 받아,
        추론에 필요한 모델, 입력 데이터 경로 및
        추론 하이퍼파라미터를 구성합니다.

        Args:
            config (dict):
                다음 정보를 포함한 설정 딕셔너리
                - inference_args.model_path
                - inference_args.img_dir
                - inference_args.conf (optional)
                - inference_args.iou (optional)
                - inference_args.max_det (optional)
                - inference_args.save (optional)
                - paths.base_dir

            mapper (CategoryMapper):
                YOLO class_id ↔ COCO category_id 변환을 담당하는 매퍼 객체

        초기화 시 수행 작업:
            - YOLO 모델 로드
            - 추론 대상 이미지 디렉토리 설정
            - confidence / IoU / max_det 등 추론 파라미터 로드
        """
        self.cfg = config
        self.mapper = mapper

        infer_cfg = config["inference_args"]
        base = config["paths"]["base_dir"]

        # model
        self.model_path = os.path.join(base, infer_cfg["model_path"])
        self.model = YOLO(self.model_path)

        # inference params
        self.img_dir = os.path.join(base, infer_cfg["img_dir"])
        self.conf = infer_cfg.get("conf", 0.25)
        self.iou = infer_cfg.get("iou", 0.7)
        self.max_det = infer_cfg.get("max_det", 10)
        self.save = infer_cfg.get("save", False)

        print(f"[Predictor] model → {self.model_path}")
        print(f"[Predictor] img_dir → {self.img_dir}")

    def predict_folder(self):
        """
        지정된 이미지 디렉토리 내의 모든 이미지에 대해
        YOLO 객체 탐지 추론을 수행합니다.

        수행 내용:
            - 이미지 파일 목록을 정렬하여 순차적으로 처리
            - 각 이미지에 대해 YOLO 모델 추론 실행
            - 예측된 bounding box 정보를 COCO 형식에 맞게 파싱
            - CategoryMapper를 사용하여 YOLO class_id를 COCO category_id로 변환

        출력 결과 형식:
            {
                "0001.png": [
                    {
                        "image_id": 1,
                        "category_id": 1234,
                        "bbox": [x, y, w, h],
                        "score": 0.87
                    },
                    ...
                ],
                ...
            }

        주의 사항:
            - 이미지 파일명은 숫자 형태라고 가정합니다
            (예: "1.png" → image_id = 1)
            - bbox 좌표는 원본 이미지 기준의 pixel 단위입니다

        Args:
            None

        Returns:
            dict:
                이미지 파일명을 key로 하고,
                해당 이미지의 예측 결과 리스트를 value로 가지는 딕셔너리
        """
        outputs = {}
        
        infer_kwargs = {
            "conf": self.conf,
            "iou": self.iou,
            "max_det": self.max_det,
            "save": self.save
        }

        for img_name in sorted(os.listdir(self.img_dir)):
            if not img_name.lower().endswith((".png", ".jpg", ".jpeg")):
                continue

            img_path = os.path.join(self.img_dir, img_name)

            results = self.model.predict(
                source=img_path,
                device=0 if torch.cuda.is_available() else "cpu",
                **infer_kwargs
            )

            parsed = []
            r = results[0]

            # 파일명이 숫자라고 가정 (대회 포맷)
            image_id = int(os.path.splitext(img_name)[0])

            for box in r.boxes:
                cls_id = int(box.cls[0])
                cid = self.mapper.yolo_to_category_fn(cls_id)

                x1, y1, x2, y2 = box.xyxy[0]

                parsed.append({
                    "image_id": image_id,
                    "category_id": cid,
                    "bbox": [
                        float(x1),
                        float(y1),
                        float(x2 - x1),
                        float(y2 - y1)
                    ],
                    "score": float(box.conf[0])
                })

            outputs[img_name] = parsed

        print(f"[Predictor] total images: {len(outputs)}")
        
        return outputs