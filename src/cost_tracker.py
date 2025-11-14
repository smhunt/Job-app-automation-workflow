"""
Cost tracking and comparison utility
Helps users understand and compare API costs
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class CostTracker:
    """Track and compare API costs across providers"""

    # Pricing per 1M tokens (USD)
    PRICING = {
        'anthropic': {
            'claude-sonnet-4-5': {'input': 3.00, 'output': 15.00},
            'claude-3-5-sonnet': {'input': 3.00, 'output': 15.00},
            'claude-3-sonnet': {'input': 3.00, 'output': 15.00},
            'claude-3-haiku': {'input': 0.25, 'output': 1.25},
        },
        'openai': {
            'gpt-4o': {'input': 2.50, 'output': 10.00},
            'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
            'gpt-4-turbo': {'input': 10.00, 'output': 30.00},
        }
    }

    # Typical token usage per job application
    TYPICAL_USAGE = {
        'analysis': {'input': 2000, 'output': 500},
        'resume': {'input': 2500, 'output': 1000},
        'cover_letter': {'input': 2000, 'output': 600}
    }

    @classmethod
    def estimate_cost(cls, provider: str, model: str, use_batch: bool = False) -> Dict:
        """
        Estimate cost per job application

        Args:
            provider: 'anthropic' or 'openai'
            model: Model name
            use_batch: Whether using batch API (OpenAI only, 50% discount)

        Returns:
            Dictionary with cost breakdown
        """
        if provider not in cls.PRICING:
            raise ValueError(f"Unknown provider: {provider}")

        if model not in cls.PRICING[provider]:
            raise ValueError(f"Unknown model for {provider}: {model}")

        pricing = cls.PRICING[provider][model].copy()

        # Apply batch discount for OpenAI
        if provider == 'openai' and use_batch:
            pricing = {k: v * 0.5 for k, v in pricing.items()}

        costs = {}
        total = 0

        for task, tokens in cls.TYPICAL_USAGE.items():
            input_cost = (tokens['input'] / 1_000_000) * pricing['input']
            output_cost = (tokens['output'] / 1_000_000) * pricing['output']
            task_cost = input_cost + output_cost
            costs[task] = task_cost
            total += task_cost

        costs['total_per_job'] = total
        costs['provider'] = provider
        costs['model'] = model
        costs['mode'] = 'batch (50% off)' if (provider == 'openai' and use_batch) else 'real-time'

        return costs

    @classmethod
    def compare_all_options(cls) -> str:
        """
        Generate a comparison table of all provider/model options

        Returns:
            Formatted comparison text
        """
        output = ["Cost Comparison for Job Application Automation", "=" * 60, ""]

        # Anthropic options
        output.append("ANTHROPIC (Claude)")
        output.append("-" * 60)
        for model in cls.PRICING['anthropic'].keys():
            cost = cls.estimate_cost('anthropic', model)
            output.append(f"  {model:30} ${cost['total_per_job']:.3f} per job")
        output.append("")

        # OpenAI real-time options
        output.append("OPENAI (Real-time)")
        output.append("-" * 60)
        for model in cls.PRICING['openai'].keys():
            cost = cls.estimate_cost('openai', model, use_batch=False)
            output.append(f"  {model:30} ${cost['total_per_job']:.3f} per job")
        output.append("")

        # OpenAI batch options (50% discount)
        output.append("OPENAI (Batch API - 50% discount, 24hr processing)")
        output.append("-" * 60)
        for model in cls.PRICING['openai'].keys():
            cost = cls.estimate_cost('openai', model, use_batch=True)
            output.append(f"  {model:30} ${cost['total_per_job']:.3f} per job")
        output.append("")

        # Monthly estimates
        output.append("Monthly Cost Estimates (Real-time)")
        output.append("-" * 60)
        output.append("Applications/Month | Claude Sonnet | GPT-4o | GPT-4o-mini")
        output.append("-" * 60)

        claude_cost = cls.estimate_cost('anthropic', 'claude-3-5-sonnet')['total_per_job']
        gpt4o_cost = cls.estimate_cost('openai', 'gpt-4o')['total_per_job']
        gpt4o_mini_cost = cls.estimate_cost('openai', 'gpt-4o-mini')['total_per_job']

        for num_apps in [10, 25, 50, 100]:
            output.append(
                f"{num_apps:18} | "
                f"${claude_cost * num_apps:12.2f} | "
                f"${gpt4o_cost * num_apps:6.2f} | "
                f"${gpt4o_mini_cost * num_apps:11.2f}"
            )

        output.append("")
        output.append("RECOMMENDATIONS:")
        output.append("-" * 60)
        output.append("• Best quality: Claude Sonnet or GPT-4o")
        output.append("• Best value: GPT-4o-mini (real-time) or GPT-4o (batch)")
        output.append("• Cheapest: GPT-4o-mini with batch API (~$0.05 per job)")
        output.append("• For urgent applications: Use real-time mode")
        output.append("• For bulk processing: Use OpenAI batch API (50% off)")
        output.append("")

        return "\n".join(output)

    @classmethod
    def recommend_config(cls, budget_per_month: float, applications_per_month: int) -> Dict:
        """
        Recommend best configuration based on budget

        Args:
            budget_per_month: Monthly budget in USD
            applications_per_month: Expected applications per month

        Returns:
            Recommendation dictionary
        """
        cost_per_app = budget_per_month / applications_per_month if applications_per_month > 0 else 0

        recommendations = []

        # Check all options
        for provider in cls.PRICING.keys():
            for model in cls.PRICING[provider].keys():
                # Real-time
                cost = cls.estimate_cost(provider, model, use_batch=False)
                if cost['total_per_job'] <= cost_per_app:
                    recommendations.append({
                        'provider': provider,
                        'model': model,
                        'use_batch': False,
                        'cost_per_job': cost['total_per_job'],
                        'monthly_cost': cost['total_per_job'] * applications_per_month,
                        'mode': 'real-time'
                    })

                # Batch (OpenAI only)
                if provider == 'openai':
                    cost = cls.estimate_cost(provider, model, use_batch=True)
                    if cost['total_per_job'] <= cost_per_app:
                        recommendations.append({
                            'provider': provider,
                            'model': model,
                            'use_batch': True,
                            'cost_per_job': cost['total_per_job'],
                            'monthly_cost': cost['total_per_job'] * applications_per_month,
                            'mode': 'batch (50% off)'
                        })

        # Sort by quality (prefer Claude/GPT-4o) then by cost
        quality_order = {
            'claude-3-5-sonnet': 5,
            'gpt-4o': 4,
            'gpt-4-turbo': 3,
            'claude-3-sonnet': 2,
            'gpt-4o-mini': 1,
            'claude-3-haiku': 0
        }

        recommendations.sort(
            key=lambda x: (quality_order.get(x['model'], 0), -x['cost_per_job']),
            reverse=True
        )

        if not recommendations:
            return {
                'status': 'over_budget',
                'message': f"Budget of ${budget_per_month:.2f} for {applications_per_month} "
                          f"applications is too low. Minimum cost: "
                          f"${cls.estimate_cost('openai', 'gpt-4o-mini', True)['total_per_job'] * applications_per_month:.2f}"
            }

        best = recommendations[0]
        return {
            'status': 'ok',
            'recommendation': best,
            'alternatives': recommendations[1:5],  # Top 5 alternatives
            'message': f"Recommended: {best['provider'].title()} {best['model']} "
                      f"({best['mode']}) at ${best['cost_per_job']:.3f} per application"
        }


def print_cost_comparison():
    """Print cost comparison table"""
    print(CostTracker.compare_all_options())


def main():
    """CLI for cost estimation"""
    import argparse

    parser = argparse.ArgumentParser(description='AI Provider Cost Calculator')
    parser.add_argument('--compare', action='store_true', help='Show comparison table')
    parser.add_argument('--budget', type=float, help='Monthly budget (USD)')
    parser.add_argument('--applications', type=int, help='Expected applications per month')

    args = parser.parse_args()

    if args.compare or (not args.budget and not args.applications):
        print_cost_comparison()

    if args.budget and args.applications:
        print("\nBudget Analysis")
        print("=" * 60)
        result = CostTracker.recommend_config(args.budget, args.applications)

        if result['status'] == 'over_budget':
            print(result['message'])
        else:
            print(result['message'])
            print("\nConfiguration:")
            rec = result['recommendation']
            print(f"  provider: {rec['provider']}")
            print(f"  {'openai_model' if rec['provider'] == 'openai' else 'model'}: {rec['model']}")
            if rec['provider'] == 'openai':
                print(f"  use_batch: {rec['use_batch']}")
            print(f"\nEstimated monthly cost: ${rec['monthly_cost']:.2f}")

            if result['alternatives']:
                print("\nAlternatives:")
                for alt in result['alternatives']:
                    print(f"  • {alt['provider']} {alt['model']} ({alt['mode']}): "
                          f"${alt['cost_per_job']:.3f}/job, ${alt['monthly_cost']:.2f}/month")


if __name__ == '__main__':
    main()
