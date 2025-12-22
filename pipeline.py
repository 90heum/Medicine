from config.config import load_config
from src.data.pill_dataset_builder import PillDatasetBuilder
from src.mapping.category_mapper import CategoryMapper
from src.yolo.yolo_dataset_builder import YOLODatasetBuilder
from src.yolo.trainer import Trainer
from src.yolo.predictor import Predictor
from src.submission.submission_writer import SubmissionWriter

class Pipeline:
    """
    YOLO 기반 객체 탐지 프로젝트의 전체 학습 → 추론 → 제출 과정을
    하나의 실행 흐름으로 통합한 파이프라인 클래스입니다.

    이 클래스는 설정 파일(config.yaml)을 단일 진입점으로 사용하여,
    데이터셋 구축부터 모델 학습, 추론, 제출 파일 생성까지
    모든 단계를 순차적으로 실행합니다.

    파이프라인 구성 단계:
        1. Raw 데이터 → COCO 데이터셋 구축
        2. COCO category ↔ YOLO class 매핑 생성
        3. COCO → YOLO 학습용 데이터셋 변환
        4. YOLO 모델 학습
        5. 학습된 모델로 추론 수행
        6. 대회 제출용 CSV 파일 생성

    핵심 특징:
        - config.yaml 기반 전 단계 설정 통합 관리
        - 각 단계가 명확히 분리된 모듈 구조
        - 단일 run() 호출로 전체 파이프라인 실행 가능
        - 실험 재현성과 유지보수성을 모두 고려한 설계

    사용 목적:
        - 프로젝트 전체 실행 흐름의 중앙 오케스트레이터
        - 실험 반복 및 자동화 파이프라인 구성
        - 협업 환경에서의 명확한 실행 진입점 제공
    """


    def __init__(self, config_path: str):
        """
        Pipeline 객체를 초기화합니다.

        지정된 config 파일 경로로부터 설정을 로드하여,
        전체 파이프라인 실행에 필요한 모든 설정을 준비합니다.

        Args:
            config_path (str):
                config.yaml 파일의 경로

        초기화 시 수행 작업:
            - config 파일 로드
            - 전 단계에서 공통으로 사용될 설정 객체 생성
        """
        print(f"[Pipeline] Loading config → {config_path}")
        self.config = load_config(config_path)


    def run(self):
        """
        YOLO 객체 탐지 프로젝트의 전체 파이프라인을 순차적으로 실행합니다.

        이 메서드는 데이터 전처리부터 모델 학습, 추론,
        제출 파일 생성까지 모든 단계를 정의된 순서대로 수행합니다.

        실행 순서:
            [1] Dataset Build
                - 원본(raw) 이미지 및 annotation 데이터를
                COCO 형식 데이터셋으로 변환

            [2] Category Mapping
                - COCO category_id ↔ YOLO class_id 간
                결정적이고 재현 가능한 매핑 생성

            [3] YOLO Dataset Build
                - COCO 데이터셋을 YOLO 학습용 구조로 변환
                - YOLO txt 라벨 및 data.yaml 생성

            [4] YOLO Training
                - 설정 파일에 정의된 하이퍼파라미터로
                YOLO 모델 학습 수행

            [5] Inference
                - 학습된 모델을 사용하여
                테스트 이미지에 대한 객체 탐지 수행

            [6] Submission CSV
                - 추론 결과를 대회 제출 규격에 맞는
                CSV 파일로 변환 및 저장

        출력 결과:
            - 학습된 YOLO 모델 가중치
            - 추론 결과 dict
            - 제출용 CSV 파일

        Args:
            None

        Returns:
            None
        """
        print("\n===== [1] Dataset Build =====")
        dataset_builder = PillDatasetBuilder(self.config)
        dataset_builder.run()

        print("\n===== [2] Category Mapping =====")
        mapper = CategoryMapper(self.config)
        mapper.build_from_coco_folder()

        print("\n===== [3] YOLO Dataset Build =====")
        yolo_builder = YOLODatasetBuilder(self.config, mapper)
        yolo_builder.run()

        print("\n===== [4] YOLO Training =====")
        trainer = Trainer(self.config)
        trainer.train()

        print("\n===== [5] Inference =====")
        predictor = Predictor(self.config, mapper)
        predictions = predictor.predict_folder()

        print("\n===== [6] Submission CSV =====")
        submission_writer = SubmissionWriter(self.config)
        submission_writer.save(predictions)

        print("\n🎉 PIPELINE FINISHED SUCCESSFULLY!")