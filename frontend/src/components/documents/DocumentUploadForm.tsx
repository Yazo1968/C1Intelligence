import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react';
import { Button } from '../ui/Button';
import { Spinner } from '../ui/Spinner';
import { getDocumentStatus, uploadDocument } from '../../api/documents';
import type { DocumentStatusResponse } from '../../api/types';

interface DocumentUploadFormProps {
  projectId: string;
  onUploaded: () => void;
}

const ACCEPTED = '.pdf,.docx,.xlsx';
const POLL_INTERVAL_MS = 3_000;
const POLL_MAX_MS = 30 * 60 * 1_000; // 30 minutes

type ProcessingStatus = 'IDLE' | 'UPLOADING' | 'QUEUED' | 'EXTRACTING' | 'CLASSIFYING' | 'STORED' | 'FAILED' | 'POLL_ERROR';

const STATUS_MESSAGES: Record<ProcessingStatus, string> = {
  IDLE: '',
  UPLOADING: 'Uploading document...',
  QUEUED: 'Document queued for processing...',
  EXTRACTING: 'Extracting document content...',
  CLASSIFYING: 'Classifying document...',
  STORED: 'Document processed successfully.',
  FAILED: 'Document processing failed.',
  POLL_ERROR: 'Unable to check processing status. The document may still be processing.',
};

export function DocumentUploadForm({ projectId, onUploaded }: DocumentUploadFormProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const pollStartRef = useRef<number>(0);

  const [file, setFile] = useState<File | null>(null);
  const [notes, setNotes] = useState('');
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatus>('IDLE');
  const [error, setError] = useState<string | null>(null);

  const stopPolling = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  }, []);

  const startPolling = useCallback((docId: string) => {
    stopPolling();
    pollStartRef.current = Date.now();

    pollIntervalRef.current = setInterval(async () => {
      // Stop after 30 minutes
      if (Date.now() - pollStartRef.current > POLL_MAX_MS) {
        stopPolling();
        setProcessingStatus('POLL_ERROR');
        return;
      }

      try {
        const statusRes: DocumentStatusResponse = await getDocumentStatus(projectId, docId);
        setProcessingStatus(statusRes.status as ProcessingStatus);

        if (statusRes.status === 'STORED') {
          stopPolling();
          onUploaded();
        } else if (statusRes.status === 'FAILED') {
          stopPolling();
        }
      } catch {
        // Transient network error — keep polling, don't crash
      }
    }, POLL_INTERVAL_MS);
  }, [projectId, onUploaded, stopPolling]);

  // Cleanup on unmount
  useEffect(() => {
    return () => stopPolling();
  }, [stopPolling]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setError(null);
    setProcessingStatus('UPLOADING');

    try {
      const res = await uploadDocument(projectId, file, { upload_notes: notes || undefined });
      setProcessingStatus('QUEUED');
      setFile(null);
      setNotes('');
      if (fileRef.current) fileRef.current.value = '';
      startPolling(res.document_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setProcessingStatus('IDLE');
    }
  };

  const isProcessing = ['UPLOADING', 'QUEUED', 'EXTRACTING', 'CLASSIFYING'].includes(processingStatus);

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
      <form onSubmit={handleSubmit} className="flex items-end gap-3">
        <div className="flex-1">
          <label htmlFor="doc-file" className="block text-sm font-medium text-gray-700 mb-1">Upload Document</label>
          <input
            ref={fileRef}
            id="doc-file"
            type="file"
            accept={ACCEPTED}
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="block w-full text-sm text-gray-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border file:border-gray-300 file:text-sm file:font-medium file:bg-white file:text-navy-900 file:cursor-pointer hover:file:bg-gray-50"
          />
        </div>
        <div className="w-48">
          <input
            type="text"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Notes (optional)"
            className="block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm placeholder:text-gray-400 focus:border-navy-700 focus:outline-none focus:ring-1 focus:ring-navy-700"
          />
        </div>
        <Button type="submit" disabled={isProcessing || !file}>
          {isProcessing ? <><Spinner className="h-4 w-4 mr-2" /> Processing...</> : 'Upload'}
        </Button>
      </form>

      {isProcessing && (
        <div className="mt-3 flex items-center gap-2 text-sm text-navy-700">
          <Spinner className="h-4 w-4" />
          <span>{STATUS_MESSAGES[processingStatus]}</span>
        </div>
      )}

      {processingStatus === 'STORED' && (
        <div className="mt-3 rounded-md border p-3 text-sm bg-emerald-50 border-emerald-200 text-emerald-800">
          <p className="font-medium">{STATUS_MESSAGES.STORED}</p>
        </div>
      )}

      {processingStatus === 'FAILED' && (
        <div className="mt-3 rounded-md border p-3 text-sm bg-red-50 border-red-200 text-red-700">
          <p className="font-medium">{STATUS_MESSAGES.FAILED}</p>
        </div>
      )}

      {processingStatus === 'POLL_ERROR' && (
        <div className="mt-3 rounded-md border p-3 text-sm bg-amber-50 border-amber-200 text-amber-800">
          <p className="font-medium">{STATUS_MESSAGES.POLL_ERROR}</p>
        </div>
      )}

      {error && (
        <div className="mt-3 bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700">{error}</div>
      )}
    </div>
  );
}
