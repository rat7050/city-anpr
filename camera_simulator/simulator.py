import argparse
import asyncio
from .config import DEMO_CAMERAS
from .synthetic_generator import SyntheticGenerator

async def main():
    parser = argparse.ArgumentParser(description='City ANPR Camera Simulator')
    parser.add_argument('--mode', choices=['demo', 'continuous', 'video'], default='demo')
    parser.add_argument('--api-url', default='http://localhost:8000')
    parser.add_argument('--rate', type=int, default=10, help='Detections per minute')
    parser.add_argument('--token', help='JWT auth token', default=None)
    args = parser.parse_args()
    
    generator = SyntheticGenerator(DEMO_CAMERAS, args.api_url, args.token)
    
    if args.mode == 'demo':
        await generator.generate_demo_scenario()
    elif args.mode == 'continuous':
        await generator.run_continuous(args.rate)
    elif args.mode == 'video':
        print("Video mode not implemented in demo. Please use demo or continuous.")
    else:
        print(f"Unknown mode: {args.mode}")

if __name__ == '__main__':
    asyncio.run(main())
