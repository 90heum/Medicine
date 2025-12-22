# models/submission_writer.py
import csv
import os


class SubmissionWriter:
    """
    YOLO 추론 결과를 대회 제출용 CSV 형식으로 저장하는 클래스입니다.

    이 클래스는 Predictor에서 생성된 추론 결과(dict)를 입력으로 받아,
    대회 규격에 맞는 CSV 파일을 생성합니다.

    핵심 특징:
        - config.yaml 기반 출력 경로 및 파일명 관리
        - 이미지 이름 기준 정렬을 통한 결과 재현성 보장
        - annotation_id를 1부터 순차적으로 부여
        - float 타입 bbox 및 score 값을 명시적으로 변환하여 저장

    사용 목적:
        - 객체 탐지 대회 제출 파일 생성
        - 추론 결과의 최종 산출물 관리
        - 후처리 파이프라인의 마지막 단계
    """

    def __init__(self, config: dict):
        """
        SubmissionWriter 객체를 초기화합니다.

        설정 파일(config)로부터 CSV 출력 경로와 파일명을 불러와
        제출 파일 저장 환경을 구성합니다.

        Args:
            config (dict):
                다음 정보를 포함한 설정 딕셔너리
                - paths.base_dir
                - submission.output_dir
                - submission.filename

        초기화 시 수행 작업:
            - 출력 디렉토리 생성
            - 최종 CSV 파일 전체 경로 설정
        """
        self.cfg = config

        base = config["paths"]["base_dir"]
        sub_cfg = config["submission"]

        # 출력 경로
        self.output_dir = os.path.join(base, sub_cfg["output_dir"])
        self.filename = sub_cfg["filename"]
        self.out_csv = os.path.join(self.output_dir, self.filename)

        os.makedirs(self.output_dir, exist_ok=True)

        print(f"[SubmissionWriter] output → {self.out_csv}")


    def save(self, predictions: dict):
        """
        YOLO 추론 결과를 CSV 제출 형식으로 저장합니다.

        Predictor에서 반환된 추론 결과(dict)를 입력으로 받아,
        각 bounding box를 한 행(row)으로 변환하여 CSV 파일로 기록합니다.

        CSV 포맷:
            annotation_id, image_id, category_id,
            bbox_x, bbox_y, bbox_w, bbox_h, score

        처리 규칙:
            - image_id는 문자열 형태로 저장
            - annotation_id는 1부터 순차 증가
            - 이미지 이름 기준으로 정렬하여 저장 (재현성 확보)
            - score는 소수점 4자리까지 반올림

        Args:
            predictions (dict):
                Predictor.predict_folder()의 출력 결과
                {
                    "1.png": [
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

        Returns:
            None
        """
        rows = []
        annotation_id = 1

        # 이미지 이름 기준 정렬 (재현성)
        for img_name in sorted(predictions.keys()):
            dets = predictions[img_name]

            for det in dets:
                image_id = str(det["image_id"])
                category_id = det["category_id"]
                x, y, w, h = det["bbox"]
                score = det["score"]

                rows.append([
                    annotation_id,
                    image_id,
                    category_id,
                    float(x), float(y), float(w), float(h),
                    round(float(score), 4)
                ])

                annotation_id += 1

        with open(self.out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "annotation_id", "image_id", "category_id",
                "bbox_x", "bbox_y", "bbox_w", "bbox_h", "score"
            ])
            writer.writerows(rows)
            
        print(f"[SubmissionWriter] total rows: {len(rows)}")
        print(f"[SubmissionWriter] CSV 저장 완료 → {self.out_csv}")
