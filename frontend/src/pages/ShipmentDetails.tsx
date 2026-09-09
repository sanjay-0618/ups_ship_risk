import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, MapPin, Truck, AlertTriangle, ShieldAlert } from 'lucide-react';
import { shipmentsApi } from '../services/api';
import type { Shipment, RiskScore, ShipmentEvent } from '../types';
import RiskBadge from '../components/common/RiskBadge';
import RiskBreakdown from '../components/risk/RiskBreakdown';
import ShipmentTimeline from '../components/shipments/ShipmentTimeline';
import { formatDateTime, formatMinutes } from '../utils/formatters';

export default function ShipmentDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [shipment, setShipment] = useState<Shipment | null>(null);
  const [risk, setRisk] = useState<RiskScore | null>(null);
  const [timeline, setTimeline] = useState<ShipmentEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    
    setLoading(true);
    Promise.all([
      shipmentsApi.getById(id).catch(() => null),
      shipmentsApi.getRisk(id).catch(() => null),
      shipmentsApi.getTimeline(id).catch(() => [])
    ])
    .then(([s, r, t]) => {
      setShipment(s);
      setRisk(r);
      setTimeline(t);
    })
    .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="p-8 text-center text-gray-500">Loading...</div>;
  if (!shipment) return <div className="p-8 text-center text-red-500">Shipment not found.</div>;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button 
          onClick={() => navigate(-1)}
          className="p-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-gray-900">{shipment.tracking_number}</h1>
            <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
              {shipment.status.replace(/_/g, ' ')}
            </span>
            <RiskBadge level={shipment.risk_level} score={shipment.risk_score} />
          </div>
          <p className="text-gray-500 text-sm mt-1">Last updated: {formatDateTime(shipment.last_updated)}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Col - Context & Risk */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Route context */}
          <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm flex items-center justify-between">
            <div className="text-center flex-1">
              <MapPin className="w-6 h-6 text-gray-400 mx-auto mb-2" />
              <div className="font-semibold text-gray-900">{shipment.origin_name || shipment.origin_location_id}</div>
              <div className="text-xs text-gray-500">Origin</div>
            </div>
            
            <div className="flex-1 px-4 relative">
              <div className="absolute top-1/2 left-0 w-full h-0.5 bg-gray-200 -mt-px"></div>
              <Truck className="w-6 h-6 text-blue-500 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white px-1" />
            </div>

            <div className="text-center flex-1">
              <MapPin className="w-6 h-6 text-blue-600 mx-auto mb-2" />
              <div className="font-semibold text-gray-900">{shipment.destination_name || shipment.destination_location_id}</div>
              <div className="text-xs text-gray-500">Destination</div>
            </div>
          </div>

          {/* Alert box if SLA risk is high */}
          {shipment.sla_breach_probability > 0.5 && (
            <div className="bg-red-50 border border-red-200 p-4 rounded-xl flex items-start">
              <ShieldAlert className="w-6 h-6 text-red-600 mr-3 mt-0.5" />
              <div>
                <h4 className="font-semibold text-red-900">High Risk of SLA Breach</h4>
                <p className="text-red-700 text-sm mt-1">
                  There is a {(shipment.sla_breach_probability * 100).toFixed(0)}% probability this shipment will miss its delivery window due to expected delays of {formatMinutes(shipment.expected_delay_minutes)}.
                </p>
                <button 
                  onClick={() => navigate('/route-planner')}
                  className="mt-3 px-4 py-2 bg-white text-red-700 border border-red-200 rounded-lg text-sm font-medium hover:bg-red-50 transition-colors"
                >
                  Find Alternative Routes
                </button>
              </div>
            </div>
          )}

          {/* Risk Factors */}
          {risk && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2 bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                  <AlertTriangle className="w-5 h-5 text-gray-400 mr-2" />
                  Risk Breakdown
                </h3>
                <RiskBreakdown risk={risk} />
              </div>
            </div>
          )}
        </div>

        {/* Right Col - Timeline */}
        <div className="space-y-6">
          <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-5">Shipment Timeline</h3>
            <ShipmentTimeline events={timeline} />
          </div>
        </div>
      </div>
    </div>
  );
}
