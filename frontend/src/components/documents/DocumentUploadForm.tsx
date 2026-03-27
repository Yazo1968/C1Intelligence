import { useRef, useState, type FormEvent } from 'react';
import { Button } from '../ui/Button';
import { Spinner } from '../ui/Spinner';
import { uploadDocument } from '../../api/documents';
import type { DocumentUploadResponse } from '../../api/types';

interface DocumentUploadFormProps {
  projectId: string;
  onUploaded: () => void;
}

const ACCEPTED = '.pdf,.docx,.xlsx,.pptx,.csv,.jpg,.jpeg,.png';

export function DocumentUploadForm({ projectId, onUploaded }: DocumentUploadFormProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DocumentUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const res = await uploadDocument(projectId, file, { upload_notes: notes || undefined });
      setResult(res);
      setFile(null);
      setNotes('');
      if (fileRef.current) fileRef.current.value = '';
      onUploaded();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

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
        <Button type="submit" disabled={loading || !file}>
          {loading ? <><Spinner className="h-4 w-4 mr-2" /> Processing...</> : 'Upload'}
        </Button>
      </form>

      {loading && (
        <div className="mt-3 flex items-center gap-2 text-sm text-navy-700">
          <Spinner className="h-4 w-4" />
          <span>Uploading, classifying, and extracting metadata... This may take up to 60 seconds.</span>
        </div>
      )}

      {result && (
        <div className={`mt-3 rounded-md border p-3 text-sm ${result.status === 'STORED' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-amber-50 border-amber-200 text-amber-800'}`}>
          <p className="font-medium">
            {result.status === 'STORED' ? 'Document stored successfully' : `Status: ${result.status}`}
          </p>
          {result.classification && (
            <p className="mt-1">
              Classified as <span className="font-semibold">{result.classification.document_type_name}</span>
              {' '}({result.classification.category}, Tier {result.classification.tier})
              {' '}&mdash; Confidence: {(result.classification.confidence * 100).toFixed(0)}%
            </p>
          )}
          {result.validation_gaps && result.validation_gaps.length > 0 && (
            <div className="mt-2">
              <p className="font-medium text-amber-700">Metadata gaps:</p>
              <ul className="list-disc list-inside">
                {result.validation_gaps.map((g, i) => <li key={i}>{g.message}</li>)}
              </ul>
            </div>
          )}
          {result.error_message && <p className="mt-1 text-red-700">{result.error_message}</p>}
        </div>
      )}

      {error && (
        <div className="mt-3 bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700">{error}</div>
      )}
    </div>
  );
}
