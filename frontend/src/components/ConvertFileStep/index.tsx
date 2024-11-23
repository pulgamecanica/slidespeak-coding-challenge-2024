import { FC, useState } from 'react';
import { LoadingIndicatorIcon } from '@/icons/LoadingIndicatorIcon';

type ConvertFileStepProps = {
  file: File;
  onCancel: () => void;
  onConversionComplete: (videoUrls: string[]) => void;
};

export const ConvertFileStep: FC<ConvertFileStepProps> = ({
  file,
  onCancel,
  onConversionComplete,
}) => {
  const [isConverting, setIsConverting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const convertFile = async () => {
    setIsConverting(true);
    setErrorMessage(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/extract', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        onConversionComplete(result.task.urls);
      } else {
        setErrorMessage(result.detail || 'An error occurred during conversion.');
      }
    } catch (error) {
      setErrorMessage('Failed to convert the file.');
    } finally {
      setIsConverting(false);
    }
  };

  const formatBytes = (bytes: number, decimals = 2) => {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
  };

  return (
    <div className="flex flex-col gap-4 rounded-xl bg-white p-6 shadow-md">
      <div className="flex w-full flex-col gap-1 rounded-lg border border-gray-300 p-4 text-center">
        <p className="text-lg font-semibold text-gray-800">{file.name}</p>
        <p className="text-sm text-gray-600">{formatBytes(file.size)}</p>
      </div>
      {errorMessage && <p className="text-red-500 text-center">{errorMessage}</p>}
      <div className="flex w-full gap-3">
        <button
          type="button"
          className="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 font-semibold text-gray-700 shadow-sm"
          onClick={onCancel}
        >
          Cancel
        </button>
        <button
          type="button"
          className="flex w-full items-center justify-center rounded-lg border border-blue-600 bg-blue-600 px-4 py-2.5 font-semibold text-white shadow-sm"
          onClick={convertFile}
          disabled={isConverting}
        >
          {isConverting ? <LoadingIndicatorIcon /> : 'Convert'}
        </button>
      </div>
    </div>
  );
};
