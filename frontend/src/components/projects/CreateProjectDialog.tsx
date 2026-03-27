import { useState, type FormEvent } from 'react';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Spinner } from '../ui/Spinner';
import { createProject } from '../../api/projects';

interface CreateProjectDialogProps {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}

export function CreateProjectDialog({ open, onClose, onCreated }: CreateProjectDialogProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setError(null);
    setLoading(true);
    try {
      await createProject(name.trim(), description.trim() || undefined);
      setName('');
      setDescription('');
      onCreated();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="New Project">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Project Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g., Dubai Marina Phase 2"
          required
          autoFocus
        />
        <div className="space-y-1">
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional project description"
            rows={3}
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder:text-gray-400 focus:border-navy-700 focus:outline-none focus:ring-1 focus:ring-navy-700"
          />
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md px-3 py-2 text-sm text-red-700">{error}</div>
        )}

        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" type="button" onClick={onClose}>Cancel</Button>
          <Button type="submit" disabled={loading || !name.trim()}>
            {loading ? <Spinner className="h-4 w-4" /> : 'Create Project'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
