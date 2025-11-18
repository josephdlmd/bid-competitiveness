interface NotificationItem {
  id: number;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

interface NotificationProps {
  notifications: NotificationItem[];
}

const Notification = ({ notifications }: NotificationProps) => {
  const typeStyles: Record<NotificationItem['type'], string> = {
    success: 'bg-emerald-600 text-white',
    error: 'bg-red-600 text-white',
    warning: 'bg-amber-600 text-white',
    info: 'bg-slate-900 text-white'
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {notifications.map(notification => (
        <div
          key={notification.id}
          className={`${typeStyles[notification.type]} px-4 py-3 rounded-lg shadow-lg max-w-sm animate-slide-up text-sm font-medium`}
        >
          {notification.message}
        </div>
      ))}
    </div>
  );
};

export default Notification;
