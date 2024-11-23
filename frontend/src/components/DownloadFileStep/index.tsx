import { FC } from 'react';
import {PdfIcon} from "@/icons/PdfIcon";
import {CheckIcon} from "@/icons/CheckIcon";

type DownloadFileStepProps = {
  videoUrls: string[];
  onConvertAgain: () => void;
};

export const DownloadFileStep: FC<DownloadFileStepProps> = ({
  videoUrls,
  onConvertAgain,
}) => {
  return (
    <div className="flex flex-col gap-4 rounded-xl bg-white p-6 shadow-md">
      <div className="flex w-full items-center flex-col gap-1 rounded-lg border border-gray-300 p-4 text-center">
        <PdfIcon />
        <div className="mt-[-16px]">
          <CheckIcon />
        </div>
        <p className="text-lg font-semibold text-gray-800">Videos extracted successfully!</p>
      </div>
      <div className="flex w-full gap-3">
        <button
          type="button"
          className="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 font-semibold text-gray-700 shadow-sm disabled:cursor-not-allowed disabled:opacity-30"
          onClick={onConvertAgain}
        >
          Convert another
        </button>

        <ul className="list-disc pl-5">
          {videoUrls.map((url, index) => (
            <li key={index}>
              <a href={url} target="_blank" rel="noopener noreferrer">
                Downliad Video {index + 1}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
