# utils/performance.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Performance Monitor - Tracking Response Time & System Performance
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional, Any
from collections import deque
from functools import wraps

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Monitor performa sistem AMORIA
    - Tracking response time
    - Slow operation detection
    - Statistics collection
    - Memory usage tracking
    """
    
    def __init__(self, slow_threshold: float = 5.0):
        """
        Args:
            slow_threshold: Threshold untuk slow operation (detik)
        """
        self.slow_threshold = slow_threshold
        self.start_time = time.time()
        
        # Response time tracking
        self.response_times: List[float] = []
        self.response_times_max: deque = deque(maxlen=100)
        self.slow_operations: List[Dict] = []
        
        # Operation counters
        self.operation_counts: Dict[str, int] = {}
        self.error_counts: Dict[str, int] = {}
        
        # Performance metrics
        self.metrics: Dict[str, Any] = {
            'total_operations': 0,
            'total_errors': 0,
            'response_time': {
                'avg': 0.0,
                'max': 0.0,
                'min': 0.0,
                'p95': 0.0,
                'p99': 0.0
            },
            'memory_usage_mb': 0.0
        }
        
        # History
        self.history: deque = deque(maxlen=1000)
        
        logger.info(f"✅ PerformanceMonitor initialized (threshold: {slow_threshold}s)")
    
    def record_response_time(self, duration: float, operation: str = "unknown") -> None:
        """
        Rekam response time untuk operasi
        
        Args:
            duration: Waktu eksekusi dalam detik
            operation: Nama operasi
        """
        self.response_times.append(duration)
        self.response_times_max.append(duration)
        self.operation_counts[operation] = self.operation_counts.get(operation, 0) + 1
        self.metrics['total_operations'] += 1
        
        # Update metrics
        self._update_metrics()
        
        # Check for slow operation
        if duration > self.slow_threshold:
            slow_op = {
                'timestamp': time.time(),
                'operation': operation,
                'duration': round(duration, 2),
                'threshold': self.slow_threshold
            }
            self.slow_operations.append(slow_op)
            self.history.append(slow_op)
            
            # Keep only last 100 slow operations
            if len(self.slow_operations) > 100:
                self.slow_operations = self.slow_operations[-100:]
            
            logger.warning(f"⚠️ Slow operation detected: {operation} took {duration:.2f}s")
    
    def record_error(self, error_type: str, operation: str = "unknown") -> None:
        """
        Rekam error yang terjadi
        
        Args:
            error_type: Tipe error
            operation: Operasi saat error terjadi
        """
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.metrics['total_errors'] += 1
        
        self.history.append({
            'timestamp': time.time(),
            'type': 'error',
            'error_type': error_type,
            'operation': operation
        })
    
    def record_command_usage(self, command: str) -> None:
        """
        Rekam penggunaan command
        
        Args:
            command: Nama command
        """
        self.operation_counts[command] = self.operation_counts.get(command, 0) + 1
        self.metrics['total_operations'] += 1
    
    def _update_metrics(self) -> None:
        """Update metrics dari data yang ada"""
        if not self.response_times:
            return
        
        sorted_times = sorted(self.response_times)
        total = len(sorted_times)
        
        # Calculate percentiles
        p95_index = int(total * 0.95)
        p99_index = int(total * 0.99)
        
        self.metrics['response_time'] = {
            'avg': round(sum(self.response_times) / total, 2),
            'max': round(max(self.response_times), 2),
            'min': round(min(self.response_times), 2),
            'p95': round(sorted_times[p95_index] if p95_index < total else sorted_times[-1], 2),
            'p99': round(sorted_times[p99_index] if p99_index < total else sorted_times[-1], 2)
        }
    
    def update_memory_usage(self) -> None:
        """Update memory usage metric"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            self.metrics['memory_usage_mb'] = round(memory_mb, 2)
        except ImportError:
            # psutil not available, skip
            pass
        except Exception as e:
            logger.debug(f"Failed to get memory usage: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Dapatkan statistik performa lengkap
        
        Returns:
            Dictionary dengan semua statistik
        """
        self.update_memory_usage()
        
        uptime = time.time() - self.start_time
        uptime_hours = int(uptime / 3600)
        uptime_minutes = int((uptime % 3600) / 60)
        
        total_ops = self.metrics['total_operations']
        total_err = self.metrics['total_errors']
        
        return {
            'uptime': uptime,
            'uptime_formatted': f"{uptime_hours}j {uptime_minutes}m",
            'start_time': self.start_time,
            'total_operations': total_ops,
            'total_errors': total_err,
            'error_rate': round(total_err / max(1, total_ops), 4),
            'response_time': self.metrics['response_time'],
            'memory_usage_mb': self.metrics['memory_usage_mb'],
            'operation_counts': dict(self.operation_counts),
            'error_counts': dict(self.error_counts),
            'slow_operations': self.slow_operations[-10:],
            'recent_events': list(self.history)[-20:]
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Dapatkan status kesehatan untuk health check
        
        Returns:
            Dictionary status kesehatan
        """
        stats = self.get_stats()
        
        health = "healthy"
        issues = []
        
        if stats['error_rate'] > 0.1:
            health = "degraded"
            issues.append(f"High error rate: {stats['error_rate']:.1%}")
        
        if stats['response_time']['avg'] > 5.0:
            health = "degraded"
            issues.append(f"High response time: {stats['response_time']['avg']:.1f}s")
        
        if stats['response_time']['p95'] > 10.0:
            health = "unhealthy"
            issues.append(f"Very high p95 response time: {stats['response_time']['p95']:.1f}s")
        
        return {
            'status': health,
            'issues': issues,
            'uptime': stats['uptime_formatted'],
            'total_operations': stats['total_operations'],
            'error_rate': stats['error_rate'],
            'avg_response_time': stats['response_time']['avg'],
            'memory_usage_mb': stats['memory_usage_mb']
        }
    
    def reset(self) -> None:
        """Reset semua data monitor"""
        self.response_times = []
        self.response_times_max = deque(maxlen=100)
        self.slow_operations = []
        self.operation_counts = {}
        self.error_counts = {}
        self.history = deque(maxlen=1000)
        self.metrics = {
            'total_operations': 0,
            'total_errors': 0,
            'response_time': {'avg': 0.0, 'max': 0.0, 'min': 0.0, 'p95': 0.0, 'p99': 0.0},
            'memory_usage_mb': 0.0
        }
        self.start_time = time.time()
        logger.info("PerformanceMonitor reset")
    
    def format_stats(self) -> str:
        """
        Format statistik untuk display
        
        Returns:
            String formatted stats
        """
        stats = self.get_stats()
        
        lines = [
            "📊 **PERFORMANCE STATS**",
            "",
            f"⏱️ **Uptime:** {stats['uptime_formatted']}",
            f"📈 **Total Operations:** {stats['total_operations']}",
            f"❌ **Total Errors:** {stats['total_errors']} ({stats['error_rate']:.1%})",
            f"💾 **Memory:** {stats['memory_usage_mb']} MB",
            "",
            "⚡ **Response Time:**",
            f"   • Average: {stats['response_time']['avg']}s",
            f"   • Max: {stats['response_time']['max']}s",
            f"   • Min: {stats['response_time']['min']}s",
            f"   • p95: {stats['response_time']['p95']}s",
            f"   • p99: {stats['response_time']['p99']}s",
        ]
        
        if stats['operation_counts']:
            lines.append("")
            lines.append("📋 **Operation Counts:**")
            for op, count in sorted(stats['operation_counts'].items(), key=lambda x: x[1], reverse=True)[:5]:
                lines.append(f"   • {op}: {count}")
        
        if stats['slow_operations']:
            lines.append("")
            lines.append("🐢 **Slow Operations (last 5):**")
            for op in stats['slow_operations'][-5:]:
                lines.append(f"   • {op['operation']}: {op['duration']}s")
        
        return "\n".join(lines)


# =============================================================================
# DECORATORS
# =============================================================================

def measure_time(operation: str = None):
    """
    Decorator untuk mengukur waktu eksekusi fungsi synchronously
    
    Args:
        operation: Nama operasi (default: nama fungsi)
    
    Usage:
        @measure_time("process_message")
        def my_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                op_name = operation or func.__name__
                monitor.record_response_time(duration, op_name)
                return result
            except Exception as e:
                duration = time.time() - start
                op_name = operation or func.__name__
                monitor.record_error(type(e).__name__, op_name)
                raise
        return wrapper
    return decorator


def async_measure_time(operation: str = None):
    """
    Decorator untuk mengukur waktu eksekusi fungsi async
    
    Args:
        operation: Nama operasi (default: nama fungsi)
    
    Usage:
        @async_measure_time("process_message")
        async def my_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start
                op_name = operation or func.__name__
                monitor.record_response_time(duration, op_name)
                return result
            except Exception as e:
                duration = time.time() - start
                op_name = operation or func.__name__
                monitor.record_error(type(e).__name__, op_name)
                raise
        return wrapper
    return decorator


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """
    Dapatkan instance PerformanceMonitor (singleton)
    
    Returns:
        PerformanceMonitor instance
    """
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def reset_performance_monitor():
    """Reset performance monitor instance"""
    global _performance_monitor
    if _performance_monitor:
        _performance_monitor.reset()
    else:
        _performance_monitor = PerformanceMonitor()


__all__ = [
    'PerformanceMonitor',
    'measure_time',
    'async_measure_time',
    'get_performance_monitor',
    'reset_performance_monitor',
]
