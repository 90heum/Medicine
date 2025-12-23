# **💊 \[발표 자료\] PillPal 프로젝트 구조 분석 보고서**

## 

## **1\. 프로젝트 개요 (Overview)**

본 프로젝트는 **AI 기술을 활용한 스마트 복약 관리 솔루션**으로, 현대적인 웹 기술 스택과 고도화된 AI 파이프라인을 결합한 애플리케이션입니다.

* **플랫폼:** Next.js 15 기반 반응형 웹  
* **핵심 가치:** \* **정확성:** YOLO 모델 기반의 정밀한 알약 식별  
  * **편의성:** 복약 스케줄링 및 자동 알림 시스템  
  * **통찰력:** 성분 기반 음식 상호작용 및 대안 제안

## 

## **2\. 핵심 기술 스택 (Tech Stack)**

현대적이고 확장성이 뛰어난 스택을 채택하여 개발 효율성과 사용자 경험을 극대화했습니다.

| 구분 | 기술 스택 | 비고 |
| :---- | :---- | :---- |
| **Frontend** | **Next.js 15 (App Router)** | 최신 렌더링 최적화 및 안정성 확보 |
| **Language** | **TypeScript** | 정적 타입을 통한 코드 안정성 및 유지보수성 향상 |
| **UI/UX** | **Tailwind CSS / Shadcn UI** | 일관된 디자인 시스템 및 빠른 프로토타이핑 |
| **AI Orchestration** | **Google Genkit** | AI 워크플로우 관리 및 Firebase 통합 |
| **Backend/Inference** | **FastAPI (YOLO v8/v11)** | 고성능 AI 추론 엔진과의 실시간 통신 |

## 

## **3\. 시스템 아키텍처 및 데이터 흐름**

src 디렉토리를 중심으로 한 논리적 계층 분리 구조입니다.

### **🏢 아키텍처 계층 (Architecture Layers)**

1. **Presentation Layer (src/app, src/components)**  
   * Next.js App Router 기반의 선언적 라우팅  
   * PillRecognizer, MedicationTracker 등 독립적 모듈화 컴포넌트  
2. **Logic Layer (src/app/actions.ts)**  
   * Server Actions를 사용하여 클라이언트-서버 간 데이터 통신 간소화  
   * FastAPI와의 API 통신을 통한 이미지 추론 데이터 릴레이  
3. **AI Intelligence Layer (src/ai)**  
   * **Genkit Flows:** 복잡한 AI 로직(식별, 음식 제안)을 구조화된 흐름으로 관리  
   * 한글화된 프롬프트를 통해 사용자 맞춤형 인사이트 생성

## 

## **4\. 핵심 기능 분석 (Core Features)**

### **📸 AI 알약 인식 프로세스**

* **Input:** 사용자 카메라/갤러리 이미지 업로드  
* **Process:** Next.js Server Action → FastAPI (YOLO 추론) → Genkit 데이터 가공  
* **Output:** 알약 명칭, 효능, 주의사항 정보 반환

### **⏰ 스마트 복약 관리 시스템**

* **개인화 설정:** 복약 기간(시작/종료) 및 시간대(아침/점심/저녁) 지정  
* **자동 알림:** ReminderHandler를 통한 푸시/팝업 알림 트리거  
* **인사이트:** 성분 분석을 통한 음식 상호작용 가이드 제공

## 

## **5\. 요약 및 향후 제언 (Summary & Roadmap)**

### **✅ 강점 (Strengths)**

* **철저한 모듈화:** 비즈니스 로직과 AI 로직의 완전한 분리로 유지보수 용이성 확보  
* **실시간 연동:** FastAPI와의 긴밀한 연동으로 신속한 AI 추론 결과 제공  
* **사용자 친화적:** PT Sans 폰트 적용 및 전체 UI/AI 응답의 완벽한 한글화

### **💡 향후 개선 제언**

* **오프라인 모드:** Progressive Web App(PWA) 기술을 도입하여 네트워크 불안정 상황에서도 복약 기록 가능하도록 확장  
* **데이터 지속성:** 현재의 로직에 DB(Firestore 등)를 연동하여 장기적인 복약 히스토리 분석 기능 강화

## 

## **6\. 스크린샷**

스크린샷은 public 폴더에 저장되어 있습니다.