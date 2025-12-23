"use client";

import { useState, useRef, useEffect } from "react";
import Image from "next/image";
import { Camera, Loader2, Salad, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { handlePillRecognition, getFoodAlternatives } from "@/app/actions";
import { useToast } from "@/hooks/use-toast";
import type { RecognizePillFromImageOutput } from '@/ai/flows/pill-recognition-from-image';
import type { SuggestFoodAlternativesOutput } from '@/ai/flows/suggest-food-alternatives';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { AdBanner } from "@/components/pillpal/ad-banner";

type PillInfo = RecognizePillFromImageOutput['pills'][0];

interface PillRecognizerProps {
  reminderTrigger?: number;
}

export function PillRecognizer({ reminderTrigger = 0 }: PillRecognizerProps) {
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [pillInfo, setPillInfo] = useState<RecognizePillFromImageOutput | null>(null);
  const [selectedPill, setSelectedPill] = useState<PillInfo | null>(null);
  const [detailedAlternatives, setDetailedAlternatives] = useState<SuggestFoodAlternativesOutput | null>(null);
  const [croppedImages, setCroppedImages] = useState<string[]>([]);
  const [isRecognitionLoading, setRecognitionLoading] = useState(false);
  const [isAlternativesLoading, setAlternativesLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showBanner, setShowBanner] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  useEffect(() => {
    // Initial timer
    const timer = setTimeout(() => {
      setShowBanner(false);
    }, 9000);
    return () => clearTimeout(timer);
  }, []);

  // Watch for external reminder triggers
  useEffect(() => {
    if (reminderTrigger > 0) {
      setShowBanner(true);
      // Re-start the auto-hide timer when re-shown via reminder
      const timer = setTimeout(() => {
        setShowBanner(false);
      }, 9000);
      return () => clearTimeout(timer);
    }
  }, [reminderTrigger]);


  // Crop images when pillInfo changes
  useEffect(() => {
    if (!pillInfo || !pillInfo.pills || !imagePreview) {
      setCroppedImages([]);
      return;
    }

    const cropPills = async () => {
      const croppedParams: string[] = [];

      const img = document.createElement('img');
      img.src = imagePreview;
      await new Promise((resolve) => { img.onload = resolve; });

      for (const pill of pillInfo.pills) {
        if (pill.box && pill.box.length === 4) {
          const [x1, y1, x2, y2] = pill.box;
          const width = x2 - x1;
          const height = y2 - y1;

          if (width > 0 && height > 0) {
            const canvas = document.createElement('canvas');
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            if (ctx) {
              ctx.drawImage(img, x1, y1, width, height, 0, 0, width, height);
              croppedParams.push(canvas.toDataURL());
              continue;
            }
          }
        }
        // Fallback placeholder if no box or error
        croppedParams.push(`https://picsum.photos/seed/${Math.random()}/100/100`);
      }
      setCroppedImages(croppedParams);
    };

    cropPills();
  }, [pillInfo, imagePreview]);

  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUri = reader.result as string;
        setImagePreview(dataUri);
        recognizePill(dataUri);
      };
      reader.readAsDataURL(file);
    }
  };

  const recognizePill = async (dataUri: string) => {
    setRecognitionLoading(true);
    setPillInfo(null);
    try {
      const result = await handlePillRecognition(dataUri);
      setPillInfo(result);
    } catch (error) {
      toast({
        variant: "destructive",
        title: "인식 실패",
        description: error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.",
      });
    } finally {
      setRecognitionLoading(false);
    }
  };

  const handleAiButtonClick = async (pill: PillInfo) => {
    setSelectedPill(pill);
    setIsModalOpen(true);
    setAlternativesLoading(true);
    setDetailedAlternatives(null); // 이전 데이터 초기화

    try {
      const result = await getFoodAlternatives(pill.pillName);
      setDetailedAlternatives(result);
    } catch (error) {
      toast({
        variant: "destructive",
        title: "대체재 정보를 가져오는데 실패했습니다",
        description: error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.",
      });
      setIsModalOpen(false); // 에러 발생 시 모달 닫기
    } finally {
      setAlternativesLoading(false);
    }
  };

  return (
    <>
      <Card className="w-full shadow-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 font-headline">
            알약 인식
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col items-center gap-4">
          <input
            type="file"
            accept="image/*"
            capture="environment"
            ref={fileInputRef}
            onChange={handleImageChange}
            className="hidden"
          />
          {showBanner ? (
            <AdBanner />
          ) : imagePreview ? (
            <div className="w-full h-[350px] relative rounded-lg overflow-hidden border">
              <Image src={imagePreview} alt="Pill preview" fill style={{ objectFit: "contain" }} />
            </div>
          ) : (
            <div className="w-full h-[350px] flex flex-col items-center justify-center bg-muted/50 rounded-lg border-2 border-dashed text-center p-4">
              <Camera className="w-12 h-12 text-muted-foreground" />
              <p className="font-medium text-muted-foreground mt-2">알약 사진 업로드</p>
              <p className="text-xs text-muted-foreground mt-1">정확한 인식을 위해 알약을 가까이서 촬영해주세요.</p>
            </div>
          )}

          <Button
            onClick={() => {
              setShowBanner(false);
              fileInputRef.current?.click();
            }}
            disabled={isRecognitionLoading}
            className="w-full text-base font-bold"
          >
            {isRecognitionLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
            {imagePreview ? '다른 알약 분석하기' : '사진으로 알약 분석하기'}
          </Button>

          {isRecognitionLoading && (
            <div className="flex flex-col items-center gap-2 text-muted-foreground">
              <Loader2 className="w-8 h-8 animate-spin" />
              <p>알약을 분석 중입니다...</p>
            </div>
          )}

        </CardContent>
      </Card>

      {pillInfo && pillInfo.pills.length > 0 && (
        <div className="w-full space-y-4 animate-in fade-in-0 duration-500">
          <h2 className="text-2xl font-bold font-headline">분석 결과</h2>
          {pillInfo.pills.map((pill, index) => (
            <Card key={index} className="shadow-md">
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  <div className="w-16 h-16 relative rounded-md overflow-hidden border flex-shrink-0">
                    <Image
                      src={croppedImages[index] || `https://picsum.photos/seed/${index + 1}/100/100`}
                      alt={`${pill.pillName} preview`}
                      fill
                      style={{ objectFit: "cover" }}
                      data-ai-hint="pill medication"
                    />
                  </div>
                  <div className="flex-grow">
                    <h3 className="font-bold text-base leading-tight">{pill.pillName}</h3>
                    <Button variant="default" size="sm" className="mt-2 bg-green-600 hover:bg-green-700 flex items-center font-bold" onClick={() => handleAiButtonClick(pill)}>
                      <Sparkles className="mr-1.5 h-5 w-5" />
                      AI 분석 및 음식 대체재
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )
      }

      <Dialog open={isModalOpen} onOpenChange={(isOpen) => {
        setIsModalOpen(isOpen);
        if (!isOpen) {
          setDetailedAlternatives(null); // 모달이 닫힐 때 데이터 초기화
        }
      }}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-green-600 flex-shrink-0" />
              <span>{selectedPill?.pillName}을(를) 위한 AI 음식 대체재</span>
            </DialogTitle>
            <DialogDescription>
              이 알약의 활성 성분과 유사한 효능을 제공할 수 있는 음식들입니다.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            {isAlternativesLoading && (
              <div className="flex flex-col items-center justify-center gap-2 h-40">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
                <p className="text-muted-foreground">음식 대체재를 찾는 중...</p>
              </div>
            )}
            {detailedAlternatives && (
              <div className="space-y-4 animate-in fade-in-0 duration-500">
                <div>
                  <h4 className="font-semibold text-lg mb-2">목적</h4>
                  <p className="text-sm text-muted-foreground">{detailedAlternatives.purpose}</p>
                </div>
                <div>
                  <h4 className="font-semibold text-lg mb-2">근거</h4>
                  <p className="text-sm text-muted-foreground">{detailedAlternatives.reasoning}</p>
                </div>
                <div className="space-y-4">
                  <h4 className="font-semibold text-lg">추천 음식</h4>
                  {detailedAlternatives.foodAlternatives.map((alt) => (
                    <div key={alt.ingredient}>
                      <p className="font-medium text-sm mb-2"><span className="font-bold text-primary">{alt.ingredient}</span> 대체:</p>
                      <div className="flex flex-wrap gap-2">
                        {alt.foods.map((food, index) => (
                          <div key={index} className="flex items-center gap-2 bg-muted/50 px-3 py-1 rounded-full text-sm">
                            <Salad className="w-4 h-4 text-green-600" /> {food}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
