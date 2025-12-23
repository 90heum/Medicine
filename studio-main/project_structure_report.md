# 프로젝트 구조 분석 보고서

## 1. 개요
이 프로젝트는 **Next.js 15 (App Router)** 기반의 웹 애플리케이션으로, **Tailwind CSS**와 **Shadcn UI**를 사용하여 스타일링되었습니다. **Google Genkit**이 통합되어 AI 기능을 제공하며, 주요 목적은 알약 인식 및 복약 스케줄 관리입니다.

## 2. 핵심 기술 스택
- **Framework**: Next.js 15.3.6 (App Router 사용)
- **Language**: TypeScript
- **Styling**: Tailwind CSS, Radix UI (Shadcn), Lucide React (아이콘)
- **AI/Backend**: 
  - Google Genkit (AI 파이프라인)
  - Firebase (Genkit 연동)
  - `actions.ts`를 통한 Server Actions 사용

## 3. 디렉토리 구조 분석 (`src`)

### `src/app` (라우팅 및 페이지)
- **`layout.tsx`**: 전역 설정. Google Fonts(PT Sans)와 `Toaster`(알림)가 포함되어 있습니다.
- **`page.tsx`**: 메인 대시보드. 다음과 같은 핵심 컴포넌트들을 조합하여 구성됩니다:
  - `PillRecognizer`: 알약 인식
  - `NextDoseCountdown`: 복약 타이머
  - `MedicationTracker`, `PeriodSetter`: 복약 관리
- **`actions.ts`**: 서버 사이드 로직. 
  - **현재 상태**: 실제 FastAPI 서버(`http://localhost:8000/predict`)와 연동되어 작동합니다.
  - **구현**: 업로드된 이미지를 `FormData`로 변환하여 FastAPI 서버로 전송하고, 실제 AI 추론 결과(알약 이름 등)를 받아와 반환하도록 구현되어 있습니다.

### `src/components/pillpal` (핵심 컴포넌트)
애플리케이션의 주요 기능을 담당하는 UI 컴포넌트들입니다:
- `PillRecognizer`: 이미지 업로드 및 카메라 입력 처리.
- `MedicationTracker`: 복약 기록.
- `PeriodSetter`: 복약 기간 설정.
- `ReminderHandler`: 알림 처리.

### `src/ai` (AI 설정)
- **`flows/`**: Genkit을 사용한 AI 흐름 정의.
  - `pill-recognition-from-image.ts`: 이미지 기반 알약 인식 흐름 (구조 정의).
  - `suggest-food-alternatives.ts`: 약물과 음식 상호작용 관련 제안 AI (프롬프트가 한글화되어 있음).

## 4. 요약 및 제언
- 프로젝트는 모듈화가 잘 되어 있으며, 비즈니스 로직(`src/components/pillpal`)과 AI 로직(`src/ai`)이 분리되어 있습니다.
- 알약 인식 기능은 FastAPI 서버와 연동되어 실제 AI 모델(`YOLO`)을 통해 객체 탐지 및 알약 식별을 수행합니다.
- UI 텍스트 및 AI 응답이 모두 한글화되어 있어 국내 사용자 친화적인 경험을 제공합니다.
