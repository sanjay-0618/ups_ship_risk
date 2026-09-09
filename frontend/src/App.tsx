import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/common/Layout';
import Dashboard from './pages/Dashboard';
import RoutePlanner from './pages/RoutePlanner';
import Shipments from './pages/Shipments';
import ShipmentDetails from './pages/ShipmentDetails';
import RiskCenter from './pages/RiskCenter';
import Disruptions from './pages/Disruptions';
import Analytics from './pages/Analytics';
import ErrorBoundary from './components/common/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Layout>
          <ErrorBoundary>
            <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/route-planner" element={<RoutePlanner />} />
          <Route path="/shipments" element={<Shipments />} />
          <Route path="/shipments/:id" element={<ShipmentDetails />} />
          <Route path="/risk-center" element={<RiskCenter />} />
          <Route path="/disruptions" element={<Disruptions />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          </ErrorBoundary>
        </Layout>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
