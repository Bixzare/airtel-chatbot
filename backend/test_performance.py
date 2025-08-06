#!/usr/bin/env python3
"""
Performance testing script for the Airtel chatbot.
"""

import asyncio
import aiohttp
import time
import json
from typing import List, Dict
import statistics


class PerformanceTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = "test-session-123"

    async def test_single_request(self, message: str) -> Dict:
        """Test a single request and measure response time."""
        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat",
                json={
                    "session_id": self.session_id,
                    "message": message
                }
            ) as response:
                response_data = await response.json()
                end_time = time.time()

                return {
                    "message": message,
                    "response_time": end_time - start_time,
                    "status_code": response.status,
                    "response_length": len(response_data.get("response", "")),
                    "success": response.status == 200
                }

    async def test_multiple_requests(self, messages: List[str], delay: float = 1.0) -> List[Dict]:
        """Test multiple requests with a delay between them."""
        results = []

        for i, message in enumerate(messages):
            print(f"Testing request {i+1}/{len(messages)}: {message[:50]}...")
            result = await self.test_single_request(message)
            results.append(result)

            if i < len(messages) - 1:  # Don't delay after the last request
                await asyncio.sleep(delay)

        return results

    async def test_concurrent_requests(self, messages: List[str], concurrency: int = 5) -> List[Dict]:
        """Test multiple requests concurrently."""
        semaphore = asyncio.Semaphore(concurrency)

        async def make_request(message: str):
            async with semaphore:
                return await self.test_single_request(message)

        tasks = [make_request(msg) for msg in messages]
        results = await asyncio.gather(*tasks)
        return results

    async def get_performance_stats(self) -> Dict:
        """Get current performance statistics from the server."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/performance") as response:
                return await response.json()

    def analyze_results(self, results: List[Dict]) -> Dict:
        """Analyze test results and provide statistics."""
        if not results:
            return {}

        response_times = [r["response_time"] for r in results if r["success"]]
        response_lengths = [r["response_length"]
                            for r in results if r["success"]]

        successful_requests = sum(1 for r in results if r["success"])
        failed_requests = len(results) - successful_requests

        analysis = {
            "total_requests": len(results),
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / len(results) * 100,
            "response_times": {
                "mean": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0,
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0
            },
            "response_lengths": {
                "mean": statistics.mean(response_lengths) if response_lengths else 0,
                "median": statistics.median(response_lengths) if response_lengths else 0,
                "min": min(response_lengths) if response_lengths else 0,
                "max": max(response_lengths) if response_lengths else 0
            }
        }

        return analysis


async def main():
    """Main test function."""
    tester = PerformanceTester()

    # Test messages covering different types of queries
    test_messages = [
        "Bonjour, quels sont vos forfaits internet ?",
        "Combien coûte un forfait voix de 24h ?",
        "Comment activer Airtel Money ?",
        "Quels sont vos forfaits nocturnes ?",
        "Pouvez-vous me donner les codes d'activation ?",
        "Quels sont vos avantages par rapport aux concurrents ?",
        "Comment recharger mon compte ?",
        "Quels sont vos forfaits mensuels ?",
        "Comment transférer de l'argent ?",
        "Quels sont vos services disponibles ?"
    ]

    print("🚀 Starting Performance Test")
    print("=" * 50)

    # Get initial performance stats
    print("\n📊 Initial Performance Stats:")
    try:
        initial_stats = await tester.get_performance_stats()
        print(json.dumps(initial_stats, indent=2))
    except Exception as e:
        print(f"Could not get initial stats: {e}")

    # Test sequential requests
    print("\n🔄 Testing Sequential Requests:")
    sequential_results = await tester.test_multiple_requests(test_messages, delay=0.5)

    # Test concurrent requests
    print("\n⚡ Testing Concurrent Requests:")
    concurrent_results = await tester.test_concurrent_requests(test_messages, concurrency=3)

    # Analyze results
    print("\n📈 Performance Analysis:")
    print("=" * 50)

    sequential_analysis = tester.analyze_results(sequential_results)
    concurrent_analysis = tester.analyze_results(concurrent_results)

    print("\nSequential Requests:")
    print(f"  Success Rate: {sequential_analysis['success_rate']:.1f}%")
    print(
        f"  Average Response Time: {sequential_analysis['response_times']['mean']:.2f}s")
    print(
        f"  Median Response Time: {sequential_analysis['response_times']['median']:.2f}s")
    print(
        f"  Min/Max Response Time: {sequential_analysis['response_times']['min']:.2f}s / {sequential_analysis['response_times']['max']:.2f}s")

    print("\nConcurrent Requests:")
    print(f"  Success Rate: {concurrent_analysis['success_rate']:.1f}%")
    print(
        f"  Average Response Time: {concurrent_analysis['response_times']['mean']:.2f}s")
    print(
        f"  Median Response Time: {concurrent_analysis['response_times']['median']:.2f}s")
    print(
        f"  Min/Max Response Time: {concurrent_analysis['response_times']['min']:.2f}s / {concurrent_analysis['response_times']['max']:.2f}s")

    # Get final performance stats
    print("\n📊 Final Performance Stats:")
    try:
        final_stats = await tester.get_performance_stats()
        print(json.dumps(final_stats, indent=2))
    except Exception as e:
        print(f"Could not get final stats: {e}")

    # Detailed results
    print("\n📋 Detailed Results:")
    print("=" * 50)

    for i, result in enumerate(sequential_results):
        status = "✅" if result["success"] else "❌"
        print(
            f"{status} {i+1:2d}. {result['message'][:40]:<40} | {result['response_time']:.2f}s | {result['response_length']} chars")

if __name__ == "__main__":
    asyncio.run(main())
