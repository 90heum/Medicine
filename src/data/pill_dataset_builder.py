import os
import json
import glob
import shutil
from collections import defaultdict
import re



class PillDatasetBuilder:
    """
    알약 이미지 데이터셋을 COCO 형식 학습 데이터셋으로 구축하기 위한 전처리 파이프라인 클래스.

    이 클래스는 원본(raw) 알약 이미지와 JSON annotation 데이터를 입력으로 받아,
    다음과 같은 일련의 데이터 정제 및 변환 과정을 수행합니다.

    전체 처리 흐름:
        1. 이미지 파일명 기반으로 알약 ID를 추출
        2. 이미지에 대응하는 annotation(JSON) 존재 여부에 따라 이미지 분류
            - matched: 모든 알약 ID에 대한 annotation 존재
            - mismatched: 일부만 annotation 존재
            - no annotation: annotation 없음
        3. 이미지별 annotation JSON 수집
        4. 여러 pill 단위 JSON을 이미지 단위 COCO JSON으로 병합
        5. COCO 학습용 디렉토리 구조로 이미지 및 annotation 정리

    주요 목적:
        - 불완전한 annotation 데이터를 체계적으로 분리
        - COCO 포맷 기반의 깨끗한 학습 데이터셋 구성
        - 이후 YOLO / Detectron2 등 객체 탐지 학습 파이프라인과의 호환성 확보

    설정 방식:
        모든 경로는 config(dict) 기반으로 관리되며,
        절대 경로를 내부에서 일관되게 생성하여 실행 환경 의존성을 제거합니다.
    """
    
    def __init__(self, config: dict):
        """
        PillDatasetBuilder 객체를 초기화하고, 데이터셋 처리에 필요한
        모든 디렉토리 경로를 설정 및 생성합니다.

        Args:
            config (dict):
                데이터셋 경로 구조를 정의한 설정 딕셔너리.
                base_dir, raw, filtered, processed, coco 관련 경로 정보를 포함해야 합니다.

        초기화 시 수행 작업:
            - raw / filtered / processed / coco 관련 모든 절대 경로 구성
            - 필요한 디렉토리 자동 생성 (이미 존재 시 유지)
        """
        self.cfg = config
        self.base = config["paths"]["base_dir"]     # /Users/apple/data_process/

        # raw 폴더 경로
        raw = config["paths"]["raw"]                
        self.raw_dir = os.path.join(self.base, raw["dir"]) # /Users/apple/data_process/data/raw
        
        # 원본 데이터 경로
        self.img_dir = os.path.join(self.raw_dir, raw["image_dir"]) # /Users/apple/data_process/data/raw/train_images
        self.ann_dir = os.path.join(self.raw_dir, raw["annotation_dir"]) # # /Users/apple/data_process/data/raw/train_annotations
    
        # filtered 폴더 경로
        filtered = config["paths"]["filtered"]
        self.filtered_dir = os.path.join(self.base, filtered["dir"]) # /Users/apple/data_process/data/raw/filtered
        
        # 필터링 이미지 데이터셋 경로
        self.matched_img_dir = os.path.join(self.filtered_dir, filtered["matched_images"])
        self.mismatched_img_dir = os.path.join(self.filtered_dir, filtered["mismatched_images"])
        self.no_ann_img_dir = os.path.join(self.filtered_dir, filtered["images_only"])
    
        # 필터링 annotation 데이터셋 경로
        self.matched_ann_dir = os.path.join(self.filtered_dir, filtered["matched_annotations"])
        self.mismatched_ann_dir = os.path.join(self.filtered_dir, filtered["mismatched_annotations"])
        self.no_img_ann_dir = os.path.join(self.filtered_dir, filtered["annotations_only"])
    
        # processed 폴더 경로
        processed = config["paths"]["processed"]
        # coco 폴더 경로
        coco = config["paths"]["coco"]
        
        self.processed_dir = os.path.join(self.base, processed["dir"]) # /Users/apple/data_process/data/processed
        self.coco_dir = os.path.join(self.base, coco["dir"] ) # /Users/apple/data_process/data/processed/coco
        
        # coco 데이터셋 경로
        self.coco_img_dir = os.path.join(self.coco_dir, coco["images"])
        self.coco_mismatched_img_dir = os.path.join(self.coco_dir, coco["mismatched_images"])
        self.coco_label_dir = os.path.join(self.coco_dir, coco["labels"])
        self.coco_mismatched_label_dir = os.path.join(self.coco_dir, coco["mismatched_labels"])

        # 디렉토리 생성
        self._make_dirs()
        
        
    # 디렉토리 생성
    def _make_dirs(self):
        """
        데이터셋 처리 과정에서 사용되는 모든 디렉토리를 생성합니다.

        이 메서드는 전처리 파이프라인 전체에서 사용되는
        filtered / processed / coco 관련 디렉토리를 일괄적으로 생성합니다.

        특징:
            - os.makedirs(..., exist_ok=True) 사용
            - 이미 존재하는 디렉토리는 그대로 유지
            - 파이프라인 실행 전 환경 초기화 목적
        """
        groups = {
            "filtered": [
                self.filtered_dir,
                self.matched_img_dir,
                self.mismatched_img_dir,
                self.no_ann_img_dir,
                self.matched_ann_dir,
                self.mismatched_ann_dir,
                self.no_img_ann_dir,
            ],
            "processed": [
                self.processed_dir,
            ],
            "coco": [
                self.coco_dir,
                self.coco_img_dir,
                self.coco_mismatched_img_dir,
                self.coco_label_dir,
                self.coco_mismatched_label_dir,
            ],
        }

        for group, dirs in groups.items():
            for d in dirs:
                os.makedirs(d, exist_ok=True)

            
    # 이미지명에서 알약 ID 추출
    def extract_pill_ids(self, img_name):
        """
        이미지 파일명으로부터 알약 ID 정보를 추출합니다.
        
        주어진 이미지 파일명에서 확장자를 제거한 뒤, 'K-XXXXXX-XXXXXX-…' 형태의 알약 ID 문자열을 분리하여 
        각 알약의 개별 ID 목록과 전체 ID 문자열, 파일명 stem을 반환합니다.
        
        예시:
            img_name = "K-001900-016548-019607_0_2_0_2_70_000_200.png"
            → pill_ids = ["001900", "016548", "019607"]
            → id_part = "001900-016548-019607"
            → img_stem = "K-001900-016548-019607_0_2_0_2_70_000_200"
        
        Args:
            img_name: PNG 확장자를 포함한 이미지 파일명
        
        Returns:
            tuple:
                pill_ids (list[str]): 분리된 알약 ID들의 리스트
                id_part (str): 'K-' 제거 후 하이픈으로 이어진 알약 ID 문자열
                stem (str): 확장자를 제거한 이미지 파일명
        """
        img_stem = img_name.replace(".png", "")
        id_part = img_stem.split("_")[0].replace("K-", "")
        pill_ids = id_part.split("-")
        return pill_ids, id_part, img_stem
    
    def get_ann_folder(self, id_part):
        """
        알약 ID 문자열을 기반으로 해당하는 annotation 폴더 경로를 생성합니다.

        주어진 ID 문자열(id_part)을 이용하여 하나의 이미지에 대응하는 annotation 폴더의
        디렉토리 이름(K-xxxxxx_json)을 구성하고, 절대 경로 형태로 반환합니다.

        예시:
            id_part = "001900-016548-019607"
            → 반환: ".../train_annotations/K-001900-016548-019607_json"

        Args:
            id_part (str): "001900-016548-019607" 와 같은 알약 ID 문자열

        Returns:
            str: id_part에 해당하는 어노테이션 폴더의 전체 경로
        """
        return os.path.join(self.ann_dir, f"K-{id_part}_json")
    
    # 이미지 분류
    def classify_image(self):
        """
        학습 이미지들을 어노테이션 유무 및 매칭 여부에 따라 분류합니다.

        이 메서드는 이미지 파일명에서 알약 ID를 추출한 뒤, 해당 ID에 대응하는 어노테이션 폴더(K-xxxxxx-..._json)를 확인하여
        다음 기준에 따라 이미지를 세 가지 그룹으로 나눕니다.

        분류 기준:
            1) Matched  
            - 이미지에 포함된 모든 알약 ID(pill_ids)에 대해 정확한 JSON 어노테이션 파일이 존재하는 경우

            2) Mismatched  
            - 일부 알약 ID는 JSON이 존재하지만, 모든 JSON이 완전히 매칭되지는 않은 경우 (부분 매칭)

            3) No Annotation  
            - 어떠한 JSON 어노테이션도 존재하지 않는 경우

        분류된 이미지는 각각 다음 폴더로 복사됩니다:
            - matched_img_dir
            - mismatched_img_dir
            - no_ann_img_dir

        또한, 분류 결과(개수)를 출력합니다.

        Args:
            None

        Returns:
            None
        """
        train_images = glob.glob(os.path.join(self.img_dir, "*.png"))
        
        matched = []
        mismatched = []
        no_ann = []
        
        for img_path in train_images:
            img_name = os.path.basename(img_path)
            pill_ids, id_part, img_stem = self.extract_pill_ids(img_name)
            
            ann_folder = self.get_ann_folder(id_part)
            found_json = 0
            
            # annotation 폴더 존재 여부 확인
            if os.path.isdir(ann_folder):
                # 개별 pill ID의 JSON 파일 여부 체크
                for pid in pill_ids:
                    pill_folder = os.path.join(ann_folder, f"K-{pid}")
                    json_path = os.path.join(pill_folder, f"{img_stem}.json")
                    if os.path.isfile(json_path):
                        found_json += 1
        
            # 이미지 분류
            if found_json == len(pill_ids):
                # 완전한 매칭
                matched.append(img_name)
                shutil.copy2(img_path, os.path.join(self.matched_img_dir, img_name))
            elif found_json == 0:
                # 아예 annotation 없음
                no_ann.append(img_name)
                shutil.copy2(img_path, os.path.join(self.no_ann_img_dir, img_name))
            else:
                # 일부 pill의 annotation 없음
                mismatched.append(img_name)
                shutil.copy2(img_path, os.path.join(self.mismatched_img_dir, img_name))
        
        # 결과 출력
        print("====== 이미지 분류 결과 ======")
        print("Matched:", len(matched))
        print("Mismatched:", len(mismatched))
        print("No annotation:", len(no_ann))
        print("==============================")
    
    # annotation 파일 수집
    def collect_annotations(self, src_img_dir, out_ann_dir):
        """
        이미지 목록을 기준으로 관련된 어노테이션(JSON) 파일들을 수집하여 출력 폴더에 정리합니다.

        이 메서드는 특정 이미지 디렉토리(src_img_dir)에 있는 이미지들을 순회하면서 파일명에서 알약 ID 정보를 추출하고,
        해당 이미지에 매칭되는 JSON annotation들을 올바른 pill ID별로 out_ann_dir 아래에 모아 저장합니다.

        수행 과정:
            1. 이미지 파일명에서 알약 ID(pill_ids), id_part, stem을 추출
            2. 해당 이미지에 대응하는 어노테이션 폴더(K-id_part_json) 탐색
            3. 이미지마다 저장될 출력 폴더(out_ann_dir/<img_stem>) 생성
            4. pill_ids 별로 JSON 존재 여부 확인 후, 존재하면 pid.json 형태로 복사

        예시:
            이미지:  
                K-001900-016548-019607_0_2_0_2_70_000_200.png
            
            생성되는 출력 디렉토리 구조:  
                out_ann_dir/
                    K-001900-016548-019607_0_2_0_2_70_000_200/
                        001900.json
                        016548.json
                        019607.json

        Args:
            src_img_dir (str): 원본 이미지들이 위치한 디렉토리 경로.
            out_ann_dir (str): 매칭된 JSON 어노테이션을 저장할 출력 디렉토리.

        Returns:
            None
        """
        for img_path in glob.glob(os.path.join(src_img_dir, "*.png")): 
            img_name = os.path.basename(img_path) 
            pill_ids, id_part, img_stem = self.extract_pill_ids(img_name) 
            
            ann_root = self.get_ann_folder(id_part) 
            if not os.path.isdir(ann_root): 
                continue 
            
            img_out_dir = os.path.join(out_ann_dir, img_stem) 
            os.makedirs(img_out_dir, exist_ok=True) 
            
            for pid in pill_ids: 
                pill_folder = os.path.join(ann_root, f"K-{pid}") 
                json_path = os.path.join(pill_folder, f"{img_stem}.json") 
                if os.path.isfile(json_path): 
                    shutil.copy2(json_path, os.path.join(img_out_dir, f"{pid}.json"))

    # 이미지별 하나로 json 병합
    def merge_annotations(self, src_root, out_dir):
        """
        동일 이미지에 대해 분리되어 있는 여러 JSON annotation 파일을 하나의 COCO 형식 JSON으로 병합합니다.

        이 메서드는 src_root 디렉토리 안에 있는 이미지별 JSON 폴더를 순회하며,
        폴더 내부의 여러 pill ID 단위 JSON 파일들을 하나의 통합된 COCO JSON 파일로 합칩니다.

        병합 규칙:
            1) image 정보(images)
                - 첫 번째 JSON에서 원본 image_id, file_name, width, height 값을 사용
                - 새로 생성하지 않고 원본의 image_id를 유지함

            2) categories
                - 서로 다른 JSON에 존재하는 category들을 category_id 기준으로 중복 없이 병합
                - category_map으로 중복 여부를 관리

            3) annotations
                - 모든 어노테이션을 하나의 리스트로 합침
                - ann_id는 1부터 순차적으로 다시 부여
                - image_id는 원본 JSON의 image_id로 통일

        입력 구조 예시:
            src_root/
                K-001900-016548-019607_.../
                    001900.json
                    016548.json
                    019607.json

        출력 결과 예시:
            out_dir/
                K-001900-016548-019607_....json  (통합된 하나의 JSON)

        Args:
            src_root (str): 이미지별로 분리된 JSON 파일들이 저장된 상위 폴더 경로.
            out_dir (str): 병합된 JSON 파일을 저장할 출력 폴더 경로.

        Returns:
            None
        """
        merged_count = 0

        for img_folder in os.listdir(src_root):
            folder_path = os.path.join(src_root, img_folder)
            if not os.path.isdir(folder_path):
                continue

            json_files = glob.glob(os.path.join(folder_path, "*.json"))
            if not json_files:
                continue

            merged = {"images": [], "annotations": [], "categories": []}
            category_map = {}
            ann_id = 1
            image_id = None  # 원본 JSON에서 가져올 값

            for jp in json_files:
                with open(jp, encoding="utf-8") as f:
                    data = json.load(f)

                # 첫 JSON에서 image_id를 추출
                if image_id is None:
                    image_id = data["images"][0]["id"]

                    merged["images"].append({
                        "id": image_id,
                        "file_name": data["images"][0]["file_name"],
                        "width": data["images"][0]["width"],
                        "height": data["images"][0]["height"]
                    })

                # category 병합
                for cat in data.get("categories", []):
                    if cat["id"] not in category_map:
                        category_map[cat["id"]] = cat
                        merged["categories"].append(cat)

                # annotation 병합
                for ann in data.get("annotations", []):
                    new_ann = ann.copy()
                    new_ann["id"] = ann_id
                    new_ann["image_id"] = image_id  # 원본 이미지 ID 유지
                    merged["annotations"].append(new_ann)
                    ann_id += 1

            # 저장
            out_path = os.path.join(out_dir, f"{img_folder}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(merged, f, ensure_ascii=False, indent=2)

            merged_count += 1

        print(f"{merged_count}개 이미지의 annotation 병합 완료!")
        
    def copy_matched_images_to_coco(self):
        """
        매칭된 이미지들을 COCO 형식 데이터셋의 images 디렉토리로 복사합니다.

        이 메서드는 filtered 단계에서 'matched_images'로 분류된 이미지들을
        COCO 학습용 폴더 구조(processed/coco_style/images)에 그대로 복사하여 배치합니다.
        annotation 병합 단계에서 생성된 COCO JSON과 연결되는 실제 이미지 파일을 올바른 위치에 저장하는 역할을 합니다.

        수행 과정:
            1. matched_img_dir 에서 *.png 파일을 모두 탐색
            2. 파일명을 유지한 채 coco_style_img_dir 로 복사
            3. 덮어쓰기가 가능한 shutil.copy2 사용 (메타데이터 포함 복사)
            4. 모든 복사 작업 완료 후 로그 출력

        사용 목적:
            - 병합된 annotation JSON 파일과 동일한 이미지들이
            COCO dataset 규칙(images/ 폴더)에 정확히 위치하도록 정리하기 위함

        Args:
            None

        Returns:
            None
        """
        for img_path in glob.glob(os.path.join(self.matched_img_dir, "*.png")):
            img_name = os.path.basename(img_path)
            shutil.copy2(
                img_path,
                os.path.join(self.coco_img_dir, img_name)
            )

        print(f"matched_images → coco_style/images 복사 완료!")
        
    
    def copy_mismatched_images_to_coco(self):
        """
        매칭되지 않은 이미지(mismatched_images)를 COCO 형식 구조 내의 전용 폴더로 복사합니다.

        이 메서드는 filtered 단계에서 'mismatched_images'로 분류된 이미지들을
        COCO 스타일 데이터 구조(processed/coco_style/mismatched_images)에 복사하여 보관합니다.
        이들 이미지는 annotation이 일부만 존재하거나 불완전한 상태이며,
        추후 추가 라벨링을 거쳐 학습 데이터로 활용될 예정입니다.

        수행 과정:
            1. mismatched_img_dir 내부의 모든 PNG 파일 탐색
            2. 파일 이름을 유지한 채 coco_style_mismatched_img_dir 로 복사
            3. shutil.copy2를 사용하여 메타데이터 포함하여 복사
            4. 복사 완료 시 로그 출력

        사용 목적:
            - 불완전하게 annotation된 이미지들을 별도 보관하여 후속 라벨링 작업 가능
            - COCO 학습용 clean dataset 과 구분하기 위한 분리 저장

        Args:
            None

        Returns:
            None
        """
        for img_path in glob.glob(os.path.join(self.mismatched_img_dir, "*.png")):
            img_name = os.path.basename(img_path)
            shutil.copy2(
                img_path,
                os.path.join(self.coco_mismatched_img_dir, img_name)
            )

        print(f"mismatched_images → coco_style/mismatched_images 복사 완료!")

     
    def run(self):
        """
        알약 이미지 데이터셋 전처리 파이프라인 전체를 순차적으로 실행합니다.

        이 메서드는 PillDatasetBuilder 클래스가 제공하는 개별 전처리 단계를
        정해진 순서대로 실행하여, 원본(raw) 데이터로부터
        COCO 형식의 학습용 데이터셋을 완성합니다.

        실행 흐름:
            STEP 1) 이미지 분류
                - 이미지 파일명 기반으로 알약 ID 추출
                - annotation 존재 여부에 따라
                matched / mismatched / no annotation 이미지로 분류

            STEP 2) annotation 수집
                - matched, mismatched 이미지에 대해
                개별 pill 단위 JSON annotation 파일 수집
                - 이미지별 폴더 구조로 정리

            STEP 3) annotation 병합
                - 이미지 단위로 분리된 여러 JSON 파일을
                하나의 COCO 형식 JSON으로 병합
                - matched / mismatched 데이터를 각각 독립적으로 처리

            STEP 4) COCO style 이미지 복사
                - matched 이미지를 COCO 학습용 images 디렉토리로 복사
                - mismatched 이미지를 별도 COCO 폴더로 분리 저장

        출력 결과:
            - processed/coco/images           : 학습용 clean 이미지
            - processed/coco/labels           : 병합된 COCO annotation JSON
            - processed/coco/mismatched_images: 불완전 annotation 이미지
            - processed/coco/mismatched_labels: 불완전 annotation JSON

        사용 목적:
            - 데이터 전처리 전 과정을 단일 진입점(entry point)에서 실행
            - 파이프라인 재현성 및 실행 흐름 가독성 확보
            - 실험 및 재실행 시 동일한 데이터셋 생성 보장

        Args:
            None

        Returns:
            None
        """
        print("\n===== STEP 1: 이미지 분류 =====")
        self.classify_image()

        print("\n===== STEP 2: annotation 수집 =====")
        self.collect_annotations(self.matched_img_dir, self.matched_ann_dir)
        self.collect_annotations(self.mismatched_img_dir, self.mismatched_ann_dir)

        print("\n===== STEP 3: annotation 병합 =====")
        self.merge_annotations(self.matched_ann_dir, self.coco_label_dir)
        self.merge_annotations(self.mismatched_ann_dir, self.coco_mismatched_label_dir)
        
        print("\n===== STEP 4: COCO style 이미지 복사 =====")
        self.copy_matched_images_to_coco()
        self.copy_mismatched_images_to_coco()
        
        print("🎉 모든 처리 완료!")