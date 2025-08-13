/**
 * Debouncing utility для оптимизации API запросов
 */

export function debounce<TArgs extends readonly unknown[], TReturn>(
  func: (...args: TArgs) => TReturn,
  wait: number,
  immediate = false
): (...args: TArgs) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return function executedFunction(...args: TArgs) {
    const later = () => {
      timeout = null;
      if (!immediate) func(...args);
    };
    
    const callNow = immediate && !timeout;
    
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    
    if (callNow) func(...args);
  };
}

/**
 * Throttling utility для ограничения частоты вызовов
 */
export function throttle<TArgs extends readonly unknown[], TReturn>(
  func: (...args: TArgs) => TReturn,
  limit: number
): (...args: TArgs) => void {
  let inThrottle = false;
  
  return function executedFunction(...args: TArgs) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * Batch API calls для объединения множественных запросов
 */
export class BatchProcessor<T, R> {
  private queue: Array<{
    data: T;
    resolve: (value: R) => void;
    reject: (error: unknown) => void;
  }> = [];
  
  private processing = false;
  
  constructor(
    private processor: (batch: T[]) => Promise<R[]>,
    private delay = 100,
    private maxSize = 10
  ) {}
  
  add(data: T): Promise<R> {
    return new Promise((resolve, reject) => {
      this.queue.push({ data, resolve, reject });
      
      if (this.queue.length >= this.maxSize || !this.processing) {
        this.process();
      }
    });
  }
  
  private async process() {
    if (this.processing || this.queue.length === 0) return;
    
    this.processing = true;
    
    setTimeout(async () => {
      const batch = this.queue.splice(0, this.maxSize);
      
      try {
        const results = await this.processor(batch.map(item => item.data));
        batch.forEach((item, index) => {
          item.resolve(results[index]);
        });
      } catch (error) {
        batch.forEach(item => item.reject(error));
      }
      
      this.processing = false;
      
      // Обрабатываем оставшиеся элементы
      if (this.queue.length > 0) {
        this.process();
      }
    }, this.delay);
  }
}