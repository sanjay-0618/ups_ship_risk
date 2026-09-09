import React from 'react';
import { Inbox } from 'lucide-react';

export default function EmptyState({ message, description }: { message: string, description?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-white rounded-xl shadow-sm border border-gray-100">
      <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
        <Inbox className="w-8 h-8 text-gray-400" />
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-1">{message}</h3>
      {description && <p className="text-gray-500 max-w-sm">{description}</p>}
    </div>
  );
}
