import json
import os


class CategoryMapper:
    """
    COCO category_id와 YOLO class_id 간의 결정적(deterministic)이고
    재현 가능한 매핑을 생성·관리하는 클래스입니다.

    이 클래스는 COCO 형식 annotation(JSON)에 포함된 categories 정보를 기반으로
    YOLO 학습에 사용될 class_id(0 ~ N-1)를 일관되게 생성합니다.

    핵심 특징:
        - category_id 기준 정렬을 통해 실행 환경과 무관한 동일 매핑 보장
        - COCO ↔ YOLO 간 양방향 변환 지원
        - 매핑 결과를 JSON 파일로 저장 및 재사용 가능

    사용 목적:
        - 학습(train), 추론(inference), 결과 복원(post-processing) 전 과정에서
        동일한 클래스 기준 유지
        - YOLO 학습 시 names 리스트와 class index 불일치 문제 방지

    설정 방식:
        - config(dict) 기반으로 COCO label 디렉토리 및
        매핑 저장 경로를 일관되게 관리
    """

    def __init__(self, config:dict):
        """
        CategoryMapper 객체를 초기화합니다.

        설정 파일(config)로부터 COCO annotation 경로와
        category 매핑 저장 경로를 불러와 내부 상태를 준비합니다.

        Args:
            config (dict):
                다음 경로 정보를 포함한 설정 딕셔너리
                - paths.base_dir
                - paths.coco.dir
                - paths.coco.labels
                - paths.mapping.category_mapper

        초기화 내용:
            - COCO label 디렉토리 절대 경로 설정
            - 매핑 저장 경로 설정
            - 내부 매핑 컨테이너 초기화
        """
        
        self.cfg = config
        
        base = config["paths"]["base_dir"]
        coco = config["paths"]["coco"]
        mapping = config["paths"]["mapping"]        
        
        # COCO label 디렉토리
        self.coco_label_dir = os.path.join(base, coco["dir"], coco["labels"])
        # 매핑 저장 경로
        self.save_path = os.path.join(base, mapping["category_mapper"])
        
        self.category_to_yolo = {}  # {category_id: yolo_id}
        self.yolo_to_category = {}  # {yolo_id: category_id}
        self.yolo_names = []        # index = yolo_id

 
    def build_from_coco_folder(self, coco_label_dir: str | None = None):
        """
        COCO annotation JSON 폴더를 기반으로
        category_id ↔ YOLO class_id 매핑을 생성합니다.

        이 메서드는 지정된 COCO label 디렉토리 내의 모든 JSON 파일을 순회하며
        categories 정보를 수집한 뒤, category_id 기준으로 정렬하여
        YOLO class_id(0 ~ N-1)를 결정적으로 할당합니다.

        매핑 생성 규칙:
            - category_id 오름차순 정렬
            - 정렬된 순서대로 YOLO class_id 부여
            - 동일한 입력 데이터에 대해 항상 동일한 매핑 결과 생성

        Args:
            coco_label_dir (str | None):
                COCO annotation JSON 파일들이 위치한 디렉토리.
                None일 경우 config에서 지정한 기본 경로를 사용합니다.

        Raises:
            FileNotFoundError:
                지정된 COCO label 디렉토리가 존재하지 않을 경우
            ValueError:
                categories 정보가 하나도 발견되지 않은 경우

        Side Effects:
            - 내부 매핑 정보(category_to_yolo, yolo_to_category, yolo_names) 갱신
            - 매핑 결과를 JSON 파일로 저장
        """
        coco_label_dir = coco_label_dir or self.coco_label_dir
    
        if not os.path.isdir(coco_label_dir):
            raise FileNotFoundError(
                f"[CategoryMapper] COCO label 디렉토리 없음: {coco_label_dir}"
            )        

        category_dict = {}  # {category_id: name}

        for filename in os.listdir(coco_label_dir):
            if not filename.endswith(".json"):
                continue

            path = os.path.join(coco_label_dir, filename)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            for cat in data.get("categories", []):
                cid = int(cat["id"])
                name = cat["name"]
                category_dict[cid] = name

        if not category_dict:
            raise ValueError("[CategoryMapper] categories를 찾을 수 없습니다.")

        # 🔑 category_id 기준 정렬 → 항상 동일한 매핑
        self.category_to_yolo.clear()
        self.yolo_to_category.clear()
        self.yolo_names.clear()

        for idx, cid in enumerate(sorted(category_dict.keys())):
            name = category_dict[cid]
            self.category_to_yolo[cid] = idx
            self.yolo_to_category[idx] = cid
            self.yolo_names.append(name)

        self.save()

        print(f"[CategoryMapper] 총 {len(self.yolo_names)}개 카테고리 매핑 완료")


    def save(self, path: str | None = None):
        """
        생성된 category ↔ YOLO 매핑 정보를 JSON 파일로 저장합니다.

        저장되는 정보:
            - category_to_yolo
            - yolo_to_category
            - yolo_names

        Args:
            path (str | None):
                매핑 파일을 저장할 경로.
                None일 경우 초기화 시 설정된 save_path를 사용합니다.

        Raises:
            ValueError:
                저장 경로가 지정되지 않은 경우
        """
        path = path or self.save_path
        if path is None:
            raise ValueError("save_path가 지정되지 않았습니다.")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)

        data = {
            "category_to_yolo": self.category_to_yolo,
            "yolo_to_category": self.yolo_to_category,
            "yolo_names": self.yolo_names,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[CategoryMapper] 매핑 저장 완료 → {path}")


    def load(self, path: str | None = None):
        """
        저장된 category ↔ YOLO 매핑 JSON 파일을 로드합니다.

        JSON 파일에 저장된 문자열 key를
        내부적으로 int 타입으로 복원하여 사용합니다.

        Args:
            path (str | None):
                매핑 JSON 파일 경로.
                None일 경우 초기화 시 설정된 save_path를 사용합니다.

        Side Effects:
            - 내부 매핑 정보(category_to_yolo, yolo_to_category, yolo_names) 갱신
        """
        path = path or self.save_path
        
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        # JSON은 key가 str → int로 복원
        self.category_to_yolo = {int(k): int(v) for k, v in data["category_to_yolo"].items()}
        self.yolo_to_category = {int(k): int(v) for k, v in data["yolo_to_category"].items()}
        self.yolo_names = data["yolo_names"]

        print(f"[CategoryMapper] 매핑 로드 완료 ← {path}")


    def yolo_to_category_fn(self, yolo_id: int) -> int:
        """
        YOLO class_id를 COCO category_id로 변환합니다.

        Args:
            yolo_id (int): YOLO 모델 출력 class index

        Returns:
            int: 대응되는 COCO category_id
        """
        return self.yolo_to_category[yolo_id]


    def category_to_yolo_fn(self, category_id: int) -> int:
        """
        COCO category_id를 YOLO class_id로 변환합니다.

        Args:
            category_id (int): COCO annotation의 category_id

        Returns:
            int: 대응되는 YOLO class_id
        """
        return self.category_to_yolo[category_id]
