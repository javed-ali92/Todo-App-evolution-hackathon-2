import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlmodel import Session
from .database import engine
from typing import Dict, List, Any
import statistics


def test_single_connection() -> Dict[str, Any]:
    """
    Test a single database connection.

    Returns:
        Dict: Test results for a single connection
    """
    start_time = time.time()

    try:
        with Session(engine) as session:
            # Execute a simple query
            result = session.exec("SELECT 1 as test").first()
            success = result is not None
    except Exception as e:
        success = False
        print(f"Single connection test failed: {e}")

    end_time = time.time()
    duration = end_time - start_time

    return {
        'success': success,
        'duration': duration,
        'timestamp': start_time
    }


def test_concurrent_connections(num_threads: int = 10) -> Dict[str, Any]:
    """
    Test concurrent database connections.

    Args:
        num_threads: Number of concurrent threads to use

    Returns:
        Dict: Test results for concurrent connections
    """
    results = []

    def worker():
        return test_single_connection()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker) for _ in range(num_threads)]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    # Calculate statistics
    durations = [r['duration'] for r in results]
    success_count = sum(1 for r in results if r['success'])

    stats = {
        'total_requests': len(results),
        'successful_requests': success_count,
        'failed_requests': len(results) - success_count,
        'success_rate': success_count / len(results) if results else 0,
        'durations': durations,
        'avg_duration': statistics.mean(durations) if durations else 0,
        'min_duration': min(durations) if durations else 0,
        'max_duration': max(durations) if durations else 0,
        'median_duration': statistics.median(durations) if durations else 0,
        'p95_duration': 0,  # Placeholder for 95th percentile
    }

    # Calculate 95th percentile if we have enough data
    if len(durations) > 1:
        sorted_durations = sorted(durations)
        p95_index = int(0.95 * len(sorted_durations))
        if p95_index >= len(sorted_durations):
            p95_index = len(sorted_durations) - 1
        stats['p95_duration'] = sorted_durations[p95_index]

    return stats


def test_connection_pool_performance(num_requests: int = 50) -> Dict[str, Any]:
    """
    Test connection pool performance with multiple requests.

    Args:
        num_requests: Number of requests to make

    Returns:
        Dict: Performance test results
    """
    print(f"Testing connection pool performance with {num_requests} requests...")

    # Test sequential requests
    start_time = time.time()
    sequential_results = []

    for i in range(num_requests):
        result = test_single_connection()
        sequential_results.append(result)
        if (i + 1) % 10 == 0:
            print(f"Completed {i + 1}/{num_requests} sequential requests")

    sequential_end_time = time.time()
    sequential_duration = sequential_end_time - start_time

    # Calculate sequential stats
    seq_durations = [r['duration'] for r in sequential_results]
    seq_success_count = sum(1 for r in sequential_results if r['success'])

    sequential_stats = {
        'total_requests': len(sequential_results),
        'successful_requests': seq_success_count,
        'failed_requests': len(sequential_results) - seq_success_count,
        'success_rate': seq_success_count / len(sequential_results) if sequential_results else 0,
        'total_duration': sequential_duration,
        'avg_request_duration': statistics.mean(seq_durations) if seq_durations else 0,
        'requests_per_second': len(sequential_results) / sequential_duration if sequential_duration > 0 else 0
    }

    # Test concurrent requests
    concurrent_stats = test_concurrent_connections(num_threads=min(10, num_requests))

    return {
        'sequential': sequential_stats,
        'concurrent': concurrent_stats,
        'pool_config': {
            'pool_size': engine.pool.size() if hasattr(engine.pool, 'size') else 'N/A',
            'max_overflow': getattr(engine.pool, '_max_overflow', 'N/A'),
            'pool_timeout': getattr(engine.pool, '_timeout', 'N/A'),
            'pool_recycle': getattr(engine.pool, '_recycle', 'N/A')
        }
    }


def monitor_connection_pool() -> Dict[str, Any]:
    """
    Monitor the current state of the connection pool.

    Returns:
        Dict: Current pool state information
    """
    pool_state = {
        'pool_size': 'N/A',
        'checked_out': 'N/A',
        'overflow': 'N/A',
        'connections_active': 'N/A'
    }

    if hasattr(engine, 'pool'):
        pool = engine.pool

        # Different SQLAlchemy versions have different pool attributes
        if hasattr(pool, 'size'):
            pool_state['pool_size'] = pool.size()
        if hasattr(pool, '_checkedout'):
            pool_state['checked_out'] = len(pool._checkedout) if pool._checkedout else 0
        if hasattr(pool, '_overflow'):
            pool_state['overflow'] = pool._overflow
        if hasattr(pool, '_connections'):
            pool_state['connections_active'] = len(pool._connections) if pool._connections else 0

    return pool_state


def run_connection_pool_tests() -> Dict[str, Any]:
    """
    Run comprehensive connection pool tests.

    Returns:
        Dict: Comprehensive test results
    """
    print("Starting connection pool tests...")

    # Monitor initial pool state
    initial_pool_state = monitor_connection_pool()
    print(f"Initial pool state: {initial_pool_state}")

    # Run performance tests
    performance_results = test_connection_pool_performance(num_requests=20)

    # Monitor final pool state
    final_pool_state = monitor_connection_pool()
    print(f"Final pool state: {final_pool_state}")

    # Overall assessment
    overall_success = (
        performance_results['sequential']['success_rate'] == 1.0 and
        performance_results['concurrent']['success_rate'] >= 0.95  # Allow some failure in concurrent
    )

    results = {
        'initial_pool_state': initial_pool_state,
        'final_pool_state': final_pool_state,
        'performance': performance_results,
        'overall_success': overall_success,
        'assessment': 'PASSED' if overall_success else 'NEEDS_ATTENTION'
    }

    return results


def print_connection_pool_report(results: Dict[str, Any]):
    """
    Print a formatted connection pool test report.

    Args:
        results: Connection pool test results dictionary
    """
    print("=" * 70)
    print("CONNECTION POOL PERFORMANCE TEST REPORT")
    print("=" * 70)

    print(f"\nOverall Assessment: {'✅ ' + results['assessment'] if results['assessment'] == 'PASSED' else '⚠️ ' + results['assessment']}\n")

    print("POOL CONFIGURATION:")
    config = results['performance']['pool_config']
    for key, value in config.items():
        print(f"  {key}: {value}")

    print("\nPOOL STATE (before/after):")
    initial_state = results['initial_pool_state']
    final_state = results['final_pool_state']
    for key in initial_state.keys():
        print(f"  {key}: {initial_state[key]} → {final_state[key]}")

    print("\nSEQUENTIAL PERFORMANCE:")
    seq = results['performance']['sequential']
    print(f"  Requests: {seq['successful_requests']}/{seq['total_requests']} succeeded")
    print(f"  Success Rate: {seq['success_rate']:.2%}")
    print(f"  Total Duration: {seq['total_duration']:.2f}s")
    print(f"  Avg Request Time: {seq['avg_request_duration']:.4f}s")
    print(f"  Throughput: {seq['requests_per_second']:.2f} req/s")

    print("\nCONCURRENT PERFORMANCE (10 threads):")
    con = results['performance']['concurrent']
    print(f"  Requests: {con['successful_requests']}/{con['total_requests']} succeeded")
    print(f"  Success Rate: {con['success_rate']:.2%}")
    print(f"  Avg Request Time: {con['avg_duration']:.4f}s")
    print(f"  Min/Max/Median: {con['min_duration']:.4f}s/{con['max_duration']:.4f}s/{con['median_duration']:.4f}s")
    print(f"  P95 Duration: {con['p95_duration']:.4f}s")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("Testing connection pooling and performance...")
    test_results = run_connection_pool_tests()
    print_connection_pool_report(test_results)