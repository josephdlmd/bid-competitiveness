import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export const useKeyboardShortcuts = (customHandlers = {}) => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyPress = (event) => {
      // Don't trigger shortcuts when typing in inputs
      if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
        return;
      }

      // Check for custom handlers first
      const key = event.key.toLowerCase();
      const withCtrl = event.ctrlKey || event.metaKey;
      const withShift = event.shiftKey;

      // Custom handlers
      if (customHandlers[key]) {
        event.preventDefault();
        customHandlers[key](event);
        return;
      }

      // Global shortcuts
      if (withCtrl) {
        switch (key) {
          case 'k':
            event.preventDefault();
            document.querySelector('header input[type="text"]')?.focus();
            break;
          case '/':
            event.preventDefault();
            document.querySelector('header input[type="text"]')?.focus();
            break;
          default:
            break;
        }
      } else {
        switch (key) {
          case 'g':
            if (withShift) {
              // Handle 'G' for navigation shortcuts (next key)
              event.preventDefault();
            } else {
              event.preventDefault();
              // Wait for next key
              const handleNextKey = (e) => {
                switch (e.key.toLowerCase()) {
                  case 'h':
                    navigate('/');
                    break;
                  case 'b':
                    navigate('/bids');
                    break;
                  case 'c':
                    navigate('/calendar');
                    break;
                  case 'a':
                    navigate('/analytics');
                    break;
                  case 's':
                    navigate('/config');
                    break;
                  case 'l':
                    navigate('/logs');
                    break;
                  default:
                    break;
                }
                document.removeEventListener('keydown', handleNextKey);
              };
              document.addEventListener('keydown', handleNextKey);
              setTimeout(() => {
                document.removeEventListener('keydown', handleNextKey);
              }, 2000);
            }
            break;
          case '?':
            event.preventDefault();
            // Trigger help modal
            window.dispatchEvent(new CustomEvent('showKeyboardHelp'));
            break;
          case 'escape':
            // Close modals, dropdowns, etc.
            document.activeElement?.blur();
            break;
          default:
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [navigate, customHandlers]);
};

export const shortcuts = [
  { keys: ['?'], description: 'Show keyboard shortcuts', category: 'General' },
  { keys: ['Ctrl', 'K'], description: 'Focus search', category: 'General' },
  { keys: ['Escape'], description: 'Close modals / Clear focus', category: 'General' },
  { keys: ['g', 'h'], description: 'Go to Dashboard', category: 'Navigation' },
  { keys: ['g', 'b'], description: 'Go to Bid Search', category: 'Navigation' },
  { keys: ['g', 'c'], description: 'Go to Calendar', category: 'Navigation' },
  { keys: ['g', 'a'], description: 'Go to Analytics', category: 'Navigation' },
  { keys: ['g', 's'], description: 'Go to Settings', category: 'Navigation' },
  { keys: ['g', 'l'], description: 'Go to Logs', category: 'Navigation' },
];
