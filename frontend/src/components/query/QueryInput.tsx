import { useState, type FormEvent } from 'react';
import { Button } from '../ui/Button';
import { Spinner } from '../ui/Spinner';

interface QueryInputProps {
  onSubmit: (queryText: string) => void;
  loading: boolean;
}

export function QueryInput({ onSubmit, loading }: QueryInputProps) {
  const [text, setText] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!text.trim() || loading) return;
    onSubmit(text.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white border border-gray-200 rounded-lg p-4">
      <label htmlFor="query-input" className="block text-sm font-medium text-navy-900 mb-2">
        Ask a question about your project documents
      </label>
      <textarea
        id="query-input"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="e.g., What is the contract value? What are the liquidated damages provisions? When was the Notice of Claim issued?"
        rows={3}
        disabled={loading}
        className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder:text-gray-400 focus:border-navy-700 focus:outline-none focus:ring-1 focus:ring-navy-700 disabled:bg-gray-50 resize-none"
      />
      <div className="flex items-center justify-between mt-3">
        <div>
          {loading && (
            <span className="flex items-center gap-2 text-sm text-navy-700">
              <Spinner className="h-4 w-4" />
              Analyzing documents across specialist domains...
            </span>
          )}
        </div>
        <Button type="submit" disabled={loading || !text.trim()}>
          {loading ? 'Analyzing...' : 'Submit Query'}
        </Button>
      </div>
    </form>
  );
}
