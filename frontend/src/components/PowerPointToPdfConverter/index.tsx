'use client';

import { FC, useState } from 'react';
import { ChooseFileStep } from '@/components/ChooseFileStep';
import { ConvertFileStep } from '@/components/ConvertFileStep';
import { DownloadFileStep } from '@/components/DownloadFileStep';

export const PowerPointToPdfConverter: FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [videoUrls, setVideoUrls] = useState<string[]>([]);
  const [currentStep, setCurrentStep] = useState<'choose' | 'convert' | 'download'>('choose');

  const reset = () => {
    setFile(null);
    setVideoUrls([]);
    setCurrentStep('choose');
  };

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    setCurrentStep('convert');
  };

  const handleConversionComplete = (urls: string[]) => {
    setVideoUrls(urls);
    setCurrentStep('download');
  };

  return (
    <>
      {currentStep === 'choose' && <ChooseFileStep onFileSelect={handleFileSelect} />}
      {currentStep === 'convert' && file && (
        <ConvertFileStep
          file={file}
          onCancel={reset}
          onConversionComplete={handleConversionComplete}
        />
      )}
      {currentStep === 'download' && (
        <DownloadFileStep onConvertAgain={reset} videoUrls={videoUrls} />
      )}
    </>
  );
};
