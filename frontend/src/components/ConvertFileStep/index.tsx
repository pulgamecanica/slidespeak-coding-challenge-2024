import { FC, useState } from 'react';
import { LoadingIndicatorIcon } from '@/icons/LoadingIndicatorIcon';
import { cn } from '@/utils/cn';

type ConvertFileStepProps = {
  // TODO: Add the required props.
};

export const ConvertFileStep: FC<ConvertFileStepProps> = () => {
  const [isConverting, setIsConverting] = useState(false);

  // TODO: Replace with the actual file.
  const [file, setFile] = useState<File | null>(null);
  if (!file) return null;

  const convertFile = async () => {
    setIsConverting(true);

    try {
      // TODO: Convert the file to PDF via server API call.
    } finally {
      setIsConverting(false);
    }
  };

  const onCancel = () => {
    // TODO: Handle the cancel event.
  }

  const formatBytes = (bytes: number, decimals = 2) => {
    // TODO: Implement the logic to format the bytes.
    return bytes;
  }

  return (
    <div className="flex flex-col gap-4 rounded-xl bg-white p-6 shadow-md">
      <div className="flex w-full flex-col gap-1 rounded-lg border border-gray-300 p-4 text-center">
        <p className="text-lg font-semibold text-gray-800">{file.name}</p>
        <p className="text-sm text-gray-600">{formatBytes(file.size)}</p>
      </div>
      {isConverting ? (
        <Loader />
      ) : (
        <SelectBox
          value="Convert to PDF"
          description="Best quality, retains images and other assets."
        />
      )}

      <div className="flex w-full gap-3">
        <button
          type="button"
          disabled={isConverting}
          title="Cancel"
          className="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 font-semibold text-gray-700 shadow-sm disabled:cursor-not-allowed disabled:opacity-30"
          onClick={onCancel}
        >
          Cancel
        </button>
        <button
          type="button"
          disabled={isConverting}
          className="flex w-full items-center justify-center rounded-lg border border-blue-600 bg-blue-600 px-4 py-2.5 font-semibold text-white shadow-sm disabled:cursor-not-allowed disabled:opacity-30"
          onClick={convertFile}
        >
          {isConverting ? (
            <div className="animate-spin">
              <LoadingIndicatorIcon />
            </div>
          ) : (
            'Convert'
          )}
        </button>
      </div>
    </div>
  );
};

type CompressionSelectBoxProps = {
  checked?: boolean;
  value: string;
  description: string;
};

const SelectBox: FC<CompressionSelectBoxProps> = ({
  checked = true,
  value,
  description,
}) => (
);

const Loader = () => (
  <div className="flex w-full items-center gap-2 rounded-xl border border-gray-300 p-4">
    <div className="size-7 animate-spin-pretty rounded-full border-4 border-solid border-t-blue-500" />
    <p className="text-sm text-gray-700">Compressing your file...</p>
  </div>
);
