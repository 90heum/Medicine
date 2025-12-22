# yolo_dataset_builder.py
import os
import json
import yaml

class YOLODatasetBuilder:
    """
    COCO 형식 데이터셋을 YOLO 학습용 데이터셋 구조로 변환하는 클래스입니다.

    이 클래스는 COCO-style annotation(JSON)과 이미지 데이터를 입력으로 받아
    YOLO 모델 학습에 필요한 다음 요소들을 생성합니다.

    생성 대상:
        - YOLO txt 라벨 파일 (class_id, x_center, y_center, width, height)
        - YOLO 학습용 이미지 디렉토리 구조 (symlink 기반)
        - YOLO 학습용 data.yaml 설정 파일

    핵심 특징:
        - CategoryMapper를 사용하여 COCO category_id ↔ YOLO class_id를
          일관되게 변환
        - 이미지 복사를 하지 않고 symlink를 사용하여 디스크 사용량 최소화
        - config 기반 경로 관리로 재현 가능한 데이터셋 생성

    사용 목적:
        - COCO → YOLO 변환 파이프라인의 마지막 단계
        - YOLOv8 / Ultralytics 계열 모델 학습에 바로 사용 가능한 데이터셋 구성
    """
    
    
    def __init__(self, config: dict, mapper):
        """
        YOLODatasetBuilder 객체를 초기화합니다.

        설정 파일(config)과 CategoryMapper를 받아,
        COCO 데이터셋과 YOLO 데이터셋 경로를 구성하고
        필요한 디렉토리를 생성합니다.

        Args:
            config (dict):
                데이터 경로 및 YOLO 설정이 정의된 설정 딕셔너리
            mapper (CategoryMapper):
                COCO category_id ↔ YOLO class_id 변환을 담당하는 매퍼 객체

        초기화 시 수행 작업:
            - COCO images / labels 디렉토리 경로 설정
            - YOLO images/train / labels/train 디렉토리 경로 설정
            - 출력 디렉토리 자동 생성
        """
        self.cfg = config
        self.mapper = mapper
        
        self.base = config["paths"]["base_dir"]
        coco = config["paths"]["coco"]
        yolo = config["paths"]["yolo"]
        
        # COCO 데이터셋 경로
        self.coco_dir = os.path.join(self.base, coco["dir"])
        self.coco_img_dir = os.path.join(self.coco_dir, coco["images"])
        self.coco_label_dir = os.path.join(self.coco_dir, coco["labels"])
        
        # YOLO 라벨 출력 경로
        self.yolo_dir = os.path.join(self.base, yolo["dir"])
        self.yolo_img_train_dir = os.path.join(self.yolo_dir, yolo["images"], "train")
        self.yolo_label_train_dir = os.path.join(self.yolo_dir, yolo["labels"], "train")
        
        # 디렉토리 생성
        os.makedirs(self.yolo_img_train_dir, exist_ok=True)
        os.makedirs(self.yolo_label_train_dir, exist_ok=True)
    
    
    def build_labels(self):
        """
        COCO-style annotation JSON 파일을 YOLO 학습용 txt 라벨로 변환합니다.

        수행 내용:
            - COCO label 디렉토리 내의 모든 JSON 파일 순회
            - annotation의 bbox (x, y, w, h)를 YOLO 형식으로 정규화
            - CategoryMapper를 사용하여 category_id를 YOLO class_id로 변환
            - 이미지별 하나의 YOLO txt 파일 생성

        YOLO 라벨 형식:
            <class_id> <x_center> <y_center> <width> <height>
            (모든 좌표는 0~1 사이의 정규화된 값)

        Args:
            None

        Returns:
            None
        """    
        for filename in os.listdir(self.coco_label_dir):
            if not filename.endswith(".json"):
                continue

            path = os.path.join(self.coco_label_dir, filename)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            image = data["images"][0]
            img_w, img_h = image["width"], image["height"]
            img_stem = os.path.splitext(image["file_name"])[0]
            
            out_txt_path = os.path.join(self.yolo_label_train_dir, f"{img_stem}.txt")

            with open(out_txt_path, "w") as out:
                for ann in data["annotations"]:
                    x, y, w, h = ann["bbox"]
                    
                    xc = (x + w / 2) / img_w
                    yc = (y + h / 2) / img_h
                    nw = w / img_w
                    nh = h / img_h

                    yolo_id = self.mapper.category_to_yolo_fn(ann["category_id"])
                    out.write(f"{yolo_id} {xc:.6f} {yc:.6f} {nw:.6f} {nh:.6f}\n")

        print("[YOLO Dataset Builder] YOLO txt 생성 완료")
    

    def build_image_symlinks(self):
        """
        COCO 이미지 디렉토리의 이미지들을
        YOLO 학습용 이미지 디렉토리로 symlink 형태로 연결합니다.

        이 메서드는 실제 이미지 파일을 복사하지 않고
        심볼릭 링크(symlink)를 생성하여 디스크 사용량을 최소화합니다.

        수행 내용:
            - COCO images 디렉토리 내의 모든 이미지 탐색
            - YOLO images/train 디렉토리에 동일한 파일명으로 symlink 생성
            - 이미 존재하는 경우 생성 생략

        Args:
            None

        Returns:
            None
        """
        for img_name in os.listdir(self.coco_img_dir):
            if not img_name.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            
            src = os.path.join(self.coco_img_dir, img_name)
            dst = os.path.join(self.yolo_img_train_dir, img_name)

            if os.path.exists(dst):
                continue

            try: 
                os.symlink(src, dst) 
            except FileExistsError: 
                pass

        print("[YOLODatasetBuilder] 이미지 symlink 생성 완료")
    
    
    def create_yaml(self):
        """
        YOLO 학습에 사용될 data.yaml 설정 파일을 생성합니다.

        생성되는 data.yaml에는 다음 정보가 포함됩니다:
            - path  : 데이터셋 base 디렉토리
            - train : YOLO 학습 이미지 경로
            - val   : validation 이미지 경로
            - nc    : 클래스 개수
            - names : YOLO class 이름 리스트

        CategoryMapper의 yolo_names를 사용하여
        YOLO class index와 names 간의 일관성을 보장합니다.

        Args:
            None

        Returns:
            None
        """
        yaml_path = os.path.join(self.base, self.cfg["paths"]["yolo"]["data_yaml"])
        
        data_yaml = {
            "path": self.base,
            "train": os.path.relpath(self.yolo_img_train_dir, self.base),
            "val": os.path.relpath(self.yolo_img_train_dir, self.base),
            "nc": len(self.mapper.yolo_names),
            "names": self.mapper.yolo_names,
        }

        os.makedirs(os.path.dirname(yaml_path), exist_ok=True)
        
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(data_yaml, f, allow_unicode=True, sort_keys=False)

        print(f"[YOLODatasetBuilder] data.yaml 생성 완료 → {yaml_path}")
        
    def run(self):
        """
        COCO → YOLO 데이터셋 변환 파이프라인 전체를 실행합니다.

        실행 순서:
            1. COCO annotation → YOLO txt 라벨 변환
            2. COCO 이미지 → YOLO 이미지 디렉토리 symlink 생성
            3. YOLO 학습용 data.yaml 생성

        이 메서드 하나로 YOLO 학습에 필요한 모든 데이터 준비가 완료됩니다.

        Args:
            None

        Returns:
            None
        """
        self.build_labels()
        self.build_image_symlinks()
        self.create_yaml()
        print("🎉 YOLO 데이터셋 준비 완료!")