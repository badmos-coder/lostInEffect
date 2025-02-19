from dilithium.config import SecurityConfig
from dataclasses import dataclass
import time
from typing import Dict, List, Optional
import numpy as np
from collections import deque
import threading

@dataclass
class PerformanceMetrics:
    latency_ms: float
    cpu_usage: float
    memory_usage: float
    queue_size: int
    error_rate: float
    throughput: float

class MonitoringSystem:
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.metrics_window = 3600  # 1 hour
        self.metrics_history = deque(maxlen=self.metrics_window)
        self.alert_thresholds = {
            'latency_ms': 1000,
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'error_rate': 0.01,
            'queue_size': 1000
        }
        self._lock = threading.Lock()
        
    def record_metric(self, metric: PerformanceMetrics) -> None:
        """Record a new metric measurement"""
        with self._lock:
            self.metrics_history.append(metric)
            self._check_alerts(metric)
            
    def _check_alerts(self, metric: PerformanceMetrics) -> None:
        """Check if any metrics exceed thresholds"""
        for key, threshold in self.alert_thresholds.items():
            value = getattr(metric, key)
            if value > threshold:
                self._trigger_alert(key, value, threshold)
                
    def get_statistics(self) -> Dict:
        """Calculate statistical metrics"""
        with self._lock:
            metrics_array = np.array([
                [m.latency_ms, m.cpu_usage, m.memory_usage, 
                 m.queue_size, m.error_rate, m.throughput]
                for m in self.metrics_history
            ])
            
            return {
                'mean': np.mean(metrics_array, axis=0),
                'std': np.std(metrics_array, axis=0),
                'min': np.min(metrics_array, axis=0),
                'max': np.max(metrics_array, axis=0),
                'p95': np.percentile(metrics_array, 95, axis=0),
                'p99': np.percentile(metrics_array, 99, axis=0)
            } 