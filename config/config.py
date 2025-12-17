import yaml

def load_config(path: str) -> dict:
    """
    YAML 형식의 설정 파일(config.yaml)을 로드하여
    파이썬 딕셔너리로 반환합니다.

    이 함수는 프로젝트 전반에서 사용되는 모든 설정 값을
    단일 YAML 파일로 관리할 수 있도록 지원하며,
    데이터 경로, 학습 파라미터, 추론 설정 등
    파이프라인 전 단계에서 공통으로 사용됩니다.

    사용 목적:
        - 하드코딩된 경로 및 하이퍼파라미터 제거
        - 실험 설정의 중앙 집중식 관리
        - 파이프라인 재현성 확보

    Args:
        path (str):
            로드할 config.yaml 파일의 경로

    Returns:
        dict:
            YAML 파일 내용을 파싱한 설정 딕셔너리
            (중첩된 dict 구조로 반환)
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)