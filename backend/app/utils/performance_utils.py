"""
Утилиты для оптимизации производительности.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Callable
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
import psutil

from app.utils.logging_config import LoggingConfig


# Пул потоков для CPU-интенсивных задач
thread_pool = ThreadPoolExecutor(max_workers=4)


def performance_monitor(threshold_ms: float = 1000):
    """
    Декоратор для мониторинга производительности функций.
    
    Args:
        threshold_ms: Порог времени выполнения в миллисекундах для логирования
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                if duration_ms > threshold_ms:
                    LoggingConfig.get_api_logger().warning(
                        f"Slow function: {func.__name__}",
                        duration_ms=duration_ms,
                        threshold_ms=threshold_ms
                    )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                LoggingConfig.get_api_logger().error(
                    f"Function error: {func.__name__}",
                    error=str(e),
                    duration_ms=duration_ms
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                if duration_ms > threshold_ms:
                    LoggingConfig.get_api_logger().warning(
                        f"Slow function: {func.__name__}",
                        duration_ms=duration_ms,
                        threshold_ms=threshold_ms
                    )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                LoggingConfig.get_api_logger().error(
                    f"Function error: {func.__name__}",
                    error=str(e),
                    duration_ms=duration_ms
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


async def run_cpu_intensive_task(func: Callable, *args, **kwargs):
    """
    Запускает CPU-интенсивную задачу в отдельном потоке.
    
    Args:
        func: Функция для выполнения
        *args: Позиционные аргументы
        **kwargs: Именованные аргументы
    
    Returns:
        Результат выполнения функции
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(thread_pool, func, *args, **kwargs)


class BatchProcessor:
    """Процессор для пакетной обработки данных."""
    
    def __init__(self, batch_size: int = 100, max_wait_time: float = 1.0):
        """
        Args:
            batch_size: Размер пакета
            max_wait_time: Максимальное время ожидания в секундах
        """
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.pending_items: List[Any] = []
        self.pending_futures: List[asyncio.Future] = []
        self.last_batch_time = time.time()
        self._lock = asyncio.Lock()
    
    async def add_item(self, item: Any) -> Any:
        """
        Добавляет элемент в пакет для обработки.
        
        Args:
            item: Элемент для обработки
            
        Returns:
            Результат обработки элемента
        """
        async with self._lock:
            future = asyncio.Future()
            self.pending_items.append(item)
            self.pending_futures.append(future)
            
            # Проверяем условия для обработки пакета
            should_process = (
                len(self.pending_items) >= self.batch_size or
                (time.time() - self.last_batch_time) >= self.max_wait_time
            )
            
            if should_process:
                await self._process_batch()
            
            return await future
    
    async def _process_batch(self):
        """Обрабатывает накопленный пакет."""
        if not self.pending_items:
            return
        
        items = self.pending_items.copy()
        futures = self.pending_futures.copy()
        
        self.pending_items.clear()
        self.pending_futures.clear()
        self.last_batch_time = time.time()
        
        try:
            # Здесь должна быть логика обработки пакета
            # В данном примере просто возвращаем элементы как есть
            results = await self._batch_process_logic(items)
            
            # Устанавливаем результаты для всех futures
            for future, result in zip(futures, results):
                if not future.done():
                    future.set_result(result)
                    
        except Exception as e:
            # В случае ошибки уведомляем все futures
            for future in futures:
                if not future.done():
                    future.set_exception(e)
    
    async def _batch_process_logic(self, items: List[Any]) -> List[Any]:
        """
        Логика обработки пакета. Переопределите в наследниках.
        
        Args:
            items: Список элементов для обработки
            
        Returns:
            Список результатов обработки
        """
        # Пример - просто возвращаем элементы как есть
        return items


class MemoryOptimizer:
    """Утилиты для оптимизации использования памяти."""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Получает информацию об использовании памяти."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            "percent": process.memory_percent()
        }
    
    @staticmethod
    def check_memory_threshold(threshold_percent: float = 80.0) -> bool:
        """
        Проверяет, превышен ли порог использования памяти.
        
        Args:
            threshold_percent: Пороговый процент использования памяти
            
        Returns:
            True если память превышает порог
        """
        memory_usage = MemoryOptimizer.get_memory_usage()
        return memory_usage["percent"] > threshold_percent
    
    @staticmethod
    async def cleanup_if_needed(threshold_percent: float = 80.0):
        """
        Выполняет очистку памяти при превышении порога.
        
        Args:
            threshold_percent: Пороговый процент использования памяти
        """
        if MemoryOptimizer.check_memory_threshold(threshold_percent):
            import gc
            
            LoggingConfig.get_api_logger().warning(
                "High memory usage detected, running garbage collection",
                memory_usage=MemoryOptimizer.get_memory_usage()
            )
            
            # Принудительная сборка мусора
            gc.collect()
            
            # Логируем результат
            LoggingConfig.get_api_logger().info(
                "Garbage collection completed",
                memory_usage_after=MemoryOptimizer.get_memory_usage()
            )


class DatabaseOptimizer:
    """Утилиты для оптимизации работы с базой данных."""
    
    @staticmethod
    def optimize_query_batch_size(total_items: int, max_batch_size: int = 1000) -> int:
        """
        Оптимизирует размер пакета для запросов к БД.
        
        Args:
            total_items: Общее количество элементов
            max_batch_size: Максимальный размер пакета
            
        Returns:
            Оптимальный размер пакета
        """
        if total_items <= 100:
            return total_items
        elif total_items <= 1000:
            return min(100, total_items)
        else:
            return min(max_batch_size, total_items // 10)
    
    @staticmethod
    async def process_in_batches(
        items: List[Any], 
        process_func: Callable,
        batch_size: Optional[int] = None
    ) -> List[Any]:
        """
        Обрабатывает список элементов пакетами.
        
        Args:
            items: Список элементов для обработки
            process_func: Функция обработки пакета
            batch_size: Размер пакета (автоматически определяется если None)
            
        Returns:
            Список результатов обработки
        """
        if not items:
            return []
        
        if batch_size is None:
            batch_size = DatabaseOptimizer.optimize_query_batch_size(len(items))
        
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            if asyncio.iscoroutinefunction(process_func):
                batch_results = await process_func(batch)
            else:
                batch_results = process_func(batch)
            
            results.extend(batch_results)
            
            # Небольшая пауза между пакетами для снижения нагрузки
            if i + batch_size < len(items):
                await asyncio.sleep(0.01)
        
        return results


# Глобальные экземпляры
batch_processor = BatchProcessor()
memory_optimizer = MemoryOptimizer()
db_optimizer = DatabaseOptimizer()
