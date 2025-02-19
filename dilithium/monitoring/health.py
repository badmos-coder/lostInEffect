from typing import Dict, List, Optional
import psutil
import os
import time
import threading
from dilithium.config import SecurityConfig
from .metrics import PerformanceMetrics, MonitoringSystem

class HealthCheck:
    def __init__(self, config: SecurityConfig, monitoring: MonitoringSystem):
        self.config = config
        self.monitoring = monitoring
        self.health_status = "OK"
        self.last_check = time.time()
        self._start_health_monitor()
        
    def _start_health_monitor(self) -> None:
        """Start background health monitoring"""
        def monitor_loop():
            while True:
                self._check_system_health()
                time.sleep(10)  # Check every 10 seconds
                
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        
    def _check_system_health(self) -> None:
        """Perform system health check"""
        try:
            metrics = PerformanceMetrics(
                latency_ms=self._measure_latency(),
                cpu_usage=self._get_cpu_usage(),
                memory_usage=self._get_memory_usage(),
                queue_size=self._get_queue_size(),
                error_rate=self._calculate_error_rate(),
                throughput=self._measure_throughput()
            )
            
            self.monitoring.record_metric(metrics)
            self.health_status = "OK"
            self.last_check = time.time()
            
        except Exception as e:
            self.health_status = f"ERROR: {str(e)}"
            
    def get_health_report(self) -> Dict:
        """Generate comprehensive health report"""
        return {
            'status': self.health_status,
            'last_check': self.last_check,
            'metrics': self.monitoring.get_statistics(),
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_usage': psutil.disk_usage('/').percent
            }
        }

    def _get_cpu_usage(self) -> float:
        return psutil.cpu_percent(interval=1)
        
    def _get_memory_usage(self) -> float:
        return psutil.virtual_memory().percent
        
    def _measure_latency(self) -> float:
        start = time.time()
        # Simulate some work
        time.sleep(0.01)
        return (time.time() - start) * 1000  # Convert to ms
        
    def _get_queue_size(self) -> int:
        return 0  # Replace with actual queue size in production
        
    def _calculate_error_rate(self) -> float:
        return 0.001  # Replace with actual error rate in production
        
    def _measure_throughput(self) -> float:
        return 100  # Replace with actual throughput in production 