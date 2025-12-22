# trainer.py
from ultralytics import YOLO
import torch
import os


class Trainer:
    """
    config.yaml 기반으로 YOLO 모델 학습을 수행하는 클래스입니다.

    이 클래스는 Ultralytics YOLO API를 래핑하여,
    설정 파일에 정의된 모델 경로와 학습 하이퍼파라미터를 사용해
    객체 탐지 모델 학습을 일관되게 수행합니다.

    핵심 특징:
        - config(dict) 기반 학습 설정 관리
        - GPU 사용 가능 시 자동으로 CUDA 사용
        - YOLO 학습 결과를 project/name 구조로 저장

    사용 목적:
        - YOLO 학습 로직을 파이프라인에서 분리
        - 학습 설정 변경 시 코드 수정 없이 config만 수정
        - 실험 재현성 및 관리 용이성 확보
    """


    def __init__(self, config: dict):
        """
        Trainer 객체를 초기화합니다.

        설정 파일(config)로부터 YOLO 모델 경로, 학습 하이퍼파라미터,
        데이터셋 경로를 로드하여 학습 환경을 구성합니다.

        Args:
            config (dict):
                다음 정보를 포함한 설정 딕셔너리
                - train_args.model
                - train_args.epochs
                - train_args.batch
                - train_args.imgsz
                - train_args.project
                - train_args.name
                - train_args.val (optional)
                - paths.base_dir
                - paths.yolo.data_yaml

        초기화 시 수행 작업:
            - YOLO 모델 로드
            - GPU/CPU 자동 선택
            - data.yaml 경로 설정
            - 학습 하이퍼파라미터 로드
        """
        self.cfg = config
        train_cfg = config["train_args"]
        paths = config["paths"]

        # model
        self.model = YOLO(train_cfg["model"])

        # device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[Trainer] Using device: {self.device}")

        # data.yaml 경로
        self.data_yaml = os.path.join(
            paths["base_dir"],
            paths["yolo"]["data_yaml"]
        )

        # hyperparameters
        self.epochs = train_cfg["epochs"]
        self.batch = train_cfg["batch"]
        self.imgsz = train_cfg["imgsz"]
        self.project = train_cfg["project"]
        self.name = train_cfg["name"]
        self.val = train_cfg.get("val", False)

    def train(self):
        """
        YOLO 모델 학습을 수행합니다.

        이 메서드는 config.yaml에 정의된 학습 설정을 기반으로
        Ultralytics YOLO 모델의 train 메서드를 호출하여
        객체 탐지 학습을 실행합니다.

        수행 내용:
            - data.yaml 경로 전달
            - epoch, batch size, image size 설정
            - 학습 디바이스(CPU / GPU) 설정
            - validation 수행 여부 설정
            - 학습 결과를 지정된 project/name 경로에 저장

        학습 결과:
            - best.pt / last.pt 모델 파일 생성
            - runs 디렉토리에 학습 로그 및 결과 저장

        Args:
            None

        Returns:
            None
        """
        print("\n[Trainer] YOLO 학습 시작")
        print(f"[Trainer] data.yaml → {self.data_yaml}")

        train_kwargs = {
            "data": self.data_yaml,
            "epochs": self.epochs,
            "batch": self.batch,
            "imgsz": self.imgsz,
            "device": self.device,
            "project": self.project,
            "name": self.name,
            "val": self.val,
        }

        self.model.train(**train_kwargs)
        
        print(
            f"[Trainer] 학습 완료! "
            f"모델 저장 위치: {self.project}/{self.name}/weights"
        )
