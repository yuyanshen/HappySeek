import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import re
from collections import defaultdict

class LogAnalyzer:
    def __init__(self, log_file: str):
        self.log_file = log_file
        self._cache = {}

    def analyze_logs(self, hours: int = 24) -> Dict[str, Any]:
        """分析最近指定小时数的日志"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        error_count = defaultdict(int)
        request_times = []
        status_codes = defaultdict(int)

        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log_time = self._extract_timestamp(line)
                    if log_time < cutoff_time:
                        continue

                    if 'ERROR' in line:
                        error_type = self._extract_error_type(line)
                        error_count[error_type] += 1

                    if 'request completed' in line:
                        status = self._extract_status_code(line)
                        status_codes[status] += 1

                    request_time = self._extract_request_time(line)
                    if request_time:
                        request_times.append(request_time)

                except Exception:
                    continue

        return {
            'error_summary': dict(error_count),
            'status_codes': dict(status_codes),
            'avg_response_time': sum(request_times) / len(request_times) if request_times else 0,
            'total_requests': len(request_times),
            'period_hours': hours
        }

    def get_error_trends(self, days: int = 7) -> Dict[str, Dict[str, int]]:
        """获取错误趋势数据"""
        trends = defaultdict(lambda: defaultdict(int))
        cutoff_time = datetime.now() - timedelta(days=days)

        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    if 'ERROR' not in line:
                        continue

                    log_time = self._extract_timestamp(line)
                    if log_time < cutoff_time:
                        continue

                    date_str = log_time.strftime('%Y-%m-%d')
                    error_type = self._extract_error_type(line)
                    trends[date_str][error_type] += 1

                except Exception:
                    continue

        return {k: dict(v) for k, v in trends.items()}

    def get_performance_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """获取性能统计数据"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        endpoints = defaultdict(list)
        slow_requests = []

        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log_time = self._extract_timestamp(line)
                    if log_time < cutoff_time:
                        continue

                    if 'request completed' in line:
                        endpoint = self._extract_endpoint(line)
                        time = self._extract_request_time(line)
                        if endpoint and time:
                            endpoints[endpoint].append(time)
                            if time > 1.0:  # 慢请求阈值：1秒
                                slow_requests.append({
                                    'endpoint': endpoint,
                                    'time': time,
                                    'timestamp': log_time.isoformat()
                                })

                except Exception:
                    continue

        return {
            'endpoint_stats': {
                endpoint: {
                    'avg_time': sum(times) / len(times),
                    'max_time': max(times),
                    'min_time': min(times),
                    'count': len(times)
                }
                for endpoint, times in endpoints.items()
            },
            'slow_requests': sorted(slow_requests, key=lambda x: x['time'], reverse=True)[:10],
            'period_hours': hours
        }

    def export_report(self, output_path: str) -> None:
        """导出完整的分析报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'daily_analysis': self.analyze_logs(hours=24),
            'weekly_trends': self.get_error_trends(days=7),
            'performance': self.get_performance_metrics(hours=24)
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    def _extract_timestamp(self, line: str) -> datetime:
        """从日志行提取时间戳"""
        match = re.search(r'\[(.*?)\]', line)
        if match:
            return datetime.fromisoformat(match.group(1))
        raise ValueError("无法解析时间戳")

    def _extract_error_type(self, line: str) -> str:
        """从错误日志中提取错误类型"""
        match = re.search(r'ERROR.*?:(.*?):', line)
        return match.group(1).strip() if match else "Unknown Error"

    def _extract_status_code(self, line: str) -> str:
        """从请求日志中提取状态码"""
        match = re.search(r'status=(\d+)', line)
        return match.group(1) if match else "unknown"

    def _extract_request_time(self, line: str) -> Optional[float]:
        """从请求日志中提取请求时间"""
        match = re.search(r'time=([\d.]+)', line)
        return float(match.group(1)) if match else None

    def _extract_endpoint(self, line: str) -> Optional[str]:
        """从请求日志中提取API端点"""
        match = re.search(r'path="([^"]+)"', line)
        return match.group(1) if match else None

_analyzer_instance = None

def get_analyzer(log_file: str) -> LogAnalyzer:
    """获取LogAnalyzer的单例实例"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = LogAnalyzer(log_file)
    return _analyzer_instance