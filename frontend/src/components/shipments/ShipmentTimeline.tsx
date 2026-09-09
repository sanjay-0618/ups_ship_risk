import React from 'react';
import { CheckCircle2, Clock, MapPin, AlertCircle } from 'lucide-react';
import type { ShipmentEvent } from '../../types';
import { formatDateTime } from '../../utils/formatters';

interface ShipmentTimelineProps {
  events: ShipmentEvent[];
}

export default function ShipmentTimeline({ events }: ShipmentTimelineProps) {
  if (!events || events.length === 0) return null;

  return (
    <div className="flow-root">
      <ul className="-mb-8">
        {events.map((event, eventIdx) => {
          const isLast = eventIdx === events.length - 1;
          const isDelayed = event.delay_minutes > 0;
          
          let Icon = MapPin;
          let iconColor = 'text-gray-400';
          let bgColor = 'bg-gray-100';

          if (event.status === 'DELIVERED') {
            Icon = CheckCircle2;
            iconColor = 'text-green-500';
            bgColor = 'bg-green-100';
          } else if (isDelayed || event.status === 'DELAYED') {
            Icon = AlertCircle;
            iconColor = 'text-red-500';
            bgColor = 'bg-red-100';
          } else if (eventIdx === 0) { // Most recent event
            Icon = Clock;
            iconColor = 'text-blue-500';
            bgColor = 'bg-blue-100';
          }

          return (
            <li key={event.event_id}>
              <div className="relative pb-8">
                {!isLast && (
                  <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
                )}
                <div className="relative flex space-x-3">
                  <div>
                    <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${bgColor}`}>
                      <Icon className={`w-5 h-5 ${iconColor}`} aria-hidden="true" />
                    </span>
                  </div>
                  <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                    <div>
                      <p className="text-sm text-gray-900 font-medium">{event.event_type}</p>
                      <p className="text-sm text-gray-500">{event.location_name || event.location_id}</p>
                      {event.description && (
                        <p className="mt-1 text-sm text-gray-600">{event.description}</p>
                      )}
                      {isDelayed && (
                        <p className="mt-1 text-xs font-medium text-red-600">
                          Delayed by {event.delay_minutes}m
                        </p>
                      )}
                    </div>
                    <div className="whitespace-nowrap text-right text-sm text-gray-500">
                      <time dateTime={event.timestamp}>{formatDateTime(event.timestamp)}</time>
                    </div>
                  </div>
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
