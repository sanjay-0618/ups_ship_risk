import { useState, useEffect } from 'react';
import { healthApi } from '../services/api';
import type { DataSource } from '../types';

export function useDataSource() {
  const [dataSource, setDataSource] = useState<DataSource>('local');
  const [isConnected, setIsConnected] = useState(false);
  
  useEffect(() => {
    healthApi.check()
      .then(res => {
        setDataSource(res.data_source);
        setIsConnected(true);
      })
      .catch(() => {
        setDataSource('local');
        setIsConnected(false);
      });
  }, []);
  
  return { dataSource, isConnected };
}
