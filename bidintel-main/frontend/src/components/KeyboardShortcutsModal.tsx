import { useState, useEffect } from 'react';
import { X, Keyboard } from 'lucide-react';
import { Modal, Badge } from '@/components/ui';

const KeyboardShortcutsModal = () => {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === '?' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        setIsOpen(true);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  const shortcuts = [
    { keys: ['g', 'h'], description: 'Go to Dashboard' },
    { keys: ['g', 'b'], description: 'Go to Bid Search' },
    { keys: ['g', 'c'], description: 'Go to Calendar' },
    { keys: ['g', 'a'], description: 'Go to Analytics' },
    { keys: ['?'], description: 'Show keyboard shortcuts' },
  ];

  if (!isOpen) return null;

  return (
    <Modal open={isOpen} onOpenChange={setIsOpen}>
      <div className="bg-white rounded-lg max-w-2xl w-full">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div className="flex items-center space-x-2">
            <Keyboard className="w-5 h-5 text-slate-600" />
            <h2 className="text-lg font-semibold text-slate-900">Keyboard Shortcuts</h2>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="text-slate-400 hover:text-slate-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="px-6 py-4">
          <div className="space-y-3">
            {shortcuts.map((shortcut, index) => (
              <div key={index} className="flex items-center justify-between py-2">
                <span className="text-sm text-slate-700">{shortcut.description}</span>
                <div className="flex space-x-1">
                  {shortcut.keys.map((key, i) => (
                    <Badge key={i} variant="outline" className="font-mono">
                      {key}
                    </Badge>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default KeyboardShortcutsModal;
