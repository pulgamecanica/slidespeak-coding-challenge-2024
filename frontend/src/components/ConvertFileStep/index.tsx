import { FC, useState } from 'react';
import { LoadingIndicatorIcon } from '@/icons/LoadingIndicatorIcon';
import { cn } from "@/utils/cn";

type ConvertFileStepProps = {
  file: File;
  onCancel: () => void;
  onConversionComplete: (videoUrl: string) => void;
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
        const taskId = result.task_id;
        await pollForResult(taskId);
      } else {
        setErrorMessage(result.detail || 'An error occurred during conversion.');
      }
    } catch (error) {
      setErrorMessage('Failed to convert the file.');
    } finally {
      setIsConverting(false);
    }
  };

  const pollForResult = async (taskId: string) => {
    let retries = 0;
    const maxRetries = 10;

    const poll = async () => {
      try {
        const response = await fetch(`http://localhost:8000/get-result/${taskId}`);
        const result = await response.json();

        if (response.ok) {
          if (result.status === 'SUCCESS') {
            if (result.result.error) {
              setErrorMessage(result.result.error || 'Conversion failed.');
            } else if (result.result.url) {
              onConversionComplete(result.result.url);
            }
            return;
          }
        }

        retries++;
        if (retries < maxRetries) {
          setTimeout(poll, 1000); // Retry after 1 second
        } else {
          setErrorMessage('Conversion timed out. Please try again.');
        }
      } catch (error) {
        setErrorMessage('Error fetching conversion result.');
      }
    };

    poll();
    setIsConverting(false);
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

      {isConverting ? (
        <Loader />
      ) : (
        <ConversionSelectBox
          value="Extract all videos"
          description="Best quality, retains images and other assets."
        />
      )}

      {errorMessage && <p className="text-red-500 text-center">{errorMessage}</p>}

      <div className="flex w-full gap-3">
        <button
          type="button"
          className="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 font-semibold text-gray-700 shadow-sm"
          onClick={onCancel}
          disabled={isConverting}
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

const Loader = () => (
  <div className="flex w-full items-center gap-2 rounded-xl border border-gray-300 p-4">
    <div className="size-7 animate-spin-pretty rounded-full border-4 border-solid border-t-blue-500" />
    <p className="text-sm text-gray-700">Extracting the videos...</p>
  </div>
);

type ConversionSelectBoxProps = {
  checked?: boolean;
  value: string;
  description: string;
};

const ConversionSelectBox: FC<ConversionSelectBoxProps> = ({
  checked = true,
  value,
  description,
}) => (
  <label className="group flex w-full text-start cursor-pointer gap-2 rounded-xl border-2 border-blue-200 bg-blue-25 p-4">
    <input
      type="radio"
      name="compression"
      className="hidden"
      defaultChecked={checked}
    />
    <div>
      <div className="grid size-4 place-items-center rounded-full border border-blue-600">
        <div
          className={cn("h-2 w-2 rounded-full bg-blue-600 transition-opacity", {
            "opacity-0 group-hover:opacity-80": !checked,
          })}
        />
      </div>
    </div>
    <div className="flex flex-col gap-0.5">
      <span className="text-sm leading-4 text-blue-800">{value}</span>
      <span className="text-sm text-blue-700">{description}</span>
    </div>
  </label>
);
