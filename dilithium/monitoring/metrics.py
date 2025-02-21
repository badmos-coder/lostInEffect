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
        
        # Initialize with default metrics
        self.record_metric(PerformanceMetrics(
            latency_ms=0.0,
            cpu_usage=0.0,
            memory_usage=0.0,
            queue_size=0,
            error_rate=0.0,
            throughput=0.0
        ))
        
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
            if not self.metrics_history:
                return {
                    'mean': [0.0] * 6,
                    'std': [0.0] * 6,
                    'min': [0.0] * 6,
                    'max': [0.0] * 6,
                    'p95': [0.0] * 6,
                    'p99': [0.0] * 6
                }
                
            metrics_array = np.array([
                [m.latency_ms, m.cpu_usage, m.memory_usage, 
                 m.queue_size, m.error_rate, m.throughput]
                for m in self.metrics_history
            ])
            
            try:
                return {
                    'mean': np.mean(metrics_array, axis=0).tolist(),
                    'std': np.std(metrics_array, axis=0).tolist(),
                    'min': np.min(metrics_array, axis=0).tolist(),
                    'max': np.max(metrics_array, axis=0).tolist(),
                    'p95': np.percentile(metrics_array, 95, axis=0).tolist(),
                    'p99': np.percentile(metrics_array, 99, axis=0).tolist()
                }
            except Exception as e:
                # Fallback to default values if calculations fail
                return {
                    'mean': [0.0] * 6,
                    'std': [0.0] * 6,
                    'min': [0.0] * 6,
                    'max': [0.0] * 6,
                    'p95': [0.0] * 6,
                    'p99': [0.0] * 6
                }

    def _trigger_alert(self, metric_name: str, value: float, threshold: float) -> None:
        """Handle metric alerts"""
        print(f"Alert: {metric_name} exceeded threshold. Value: {value}, Threshold: {threshold}") 