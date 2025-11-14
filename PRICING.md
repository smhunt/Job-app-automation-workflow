# API Pricing Guide

Comprehensive guide to API costs for the Job Application Automation system.

## Quick Comparison

| Provider | Model | Cost per Job | Monthly (25 jobs) | Quality | Speed |
|----------|-------|--------------|-------------------|---------|-------|
| OpenAI | GPT-4o-mini (batch) | $0.04 | $1.00 | Good | 24hr |
| OpenAI | GPT-4o-mini | $0.08 | $2.00 | Good | Real-time |
| OpenAI | GPT-4o (batch) | $0.21 | $5.25 | Excellent | 24hr |
| OpenAI | GPT-4o | $0.42 | $10.50 | Excellent | Real-time |
| Anthropic | Claude Sonnet | $0.60 | $15.00 | Excellent | Real-time |

## Detailed Cost Breakdown

### Per Job Application Costs

Each job application requires three AI operations:
1. **Analysis** (fit assessment, gap identification)
2. **Resume Customization** (tailoring for the specific role)
3. **Cover Letter Generation** (personalized letter)

### Anthropic (Claude)

**Claude 3.5 Sonnet** - Best for quality
- Input: $3.00 per 1M tokens
- Output: $15.00 per 1M tokens
- **Per job: ~$0.60**
- Real-time processing only
- Excellent quality and reasoning

**Claude 3 Haiku** - Budget option
- Input: $0.25 per 1M tokens
- Output: $1.25 per 1M tokens
- **Per job: ~$0.10**
- Real-time processing
- Good quality, faster

### OpenAI (GPT-4)

**GPT-4o** - High quality
- Input: $2.50 per 1M tokens
- Output: $10.00 per 1M tokens
- **Per job (real-time): ~$0.42**
- **Per job (batch): ~$0.21** ⭐ 50% savings
- Excellent quality

**GPT-4o-mini** - Best value
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens
- **Per job (real-time): ~$0.08**
- **Per job (batch): ~$0.04** ⭐ Cheapest option!
- Good quality, very affordable

**GPT-4-Turbo** - Premium
- Input: $10.00 per 1M tokens
- Output: $30.00 per 1M tokens
- **Per job: ~$1.40**
- Highest cost, premium quality

## Batch API Explained

OpenAI's Batch API offers **50% cost savings** with one trade-off:

**Benefits:**
- 50% cheaper than real-time
- Same model quality
- Perfect for non-urgent applications

**Trade-offs:**
- Processing time: up to 24 hours
- Not suitable for urgent applications

**Best for:**
- Building a queue of applications
- Batch processing job postings overnight
- Maximum cost efficiency

## Monthly Cost Estimates

Based on different application volumes:

### 10 Applications per Month

| Option | Cost | Recommendation |
|--------|------|----------------|
| GPT-4o-mini (batch) | $0.40 | Best value |
| GPT-4o-mini | $0.80 | Good balance |
| GPT-4o (batch) | $2.10 | High quality, affordable |
| GPT-4o | $4.20 | High quality, real-time |
| Claude Sonnet | $6.00 | Premium quality |

### 25 Applications per Month

| Option | Cost | Recommendation |
|--------|------|----------------|
| GPT-4o-mini (batch) | $1.00 | Best value |
| GPT-4o-mini | $2.00 | Good balance |
| GPT-4o (batch) | $5.25 | High quality, affordable |
| GPT-4o | $10.50 | High quality, real-time |
| Claude Sonnet | $15.00 | Premium quality |

### 50 Applications per Month

| Option | Cost | Recommendation |
|--------|------|----------------|
| GPT-4o-mini (batch) | $2.00 | Best value |
| GPT-4o-mini | $4.00 | Good balance |
| GPT-4o (batch) | $10.50 | High quality, affordable |
| GPT-4o | $21.00 | High quality, real-time |
| Claude Sonnet | $30.00 | Premium quality |

### 100 Applications per Month

| Option | Cost | Recommendation |
|--------|------|----------------|
| GPT-4o-mini (batch) | $4.00 | Best value |
| GPT-4o-mini | $8.00 | Good balance |
| GPT-4o (batch) | $21.00 | High quality, affordable |
| GPT-4o | $42.00 | High quality, real-time |
| Claude Sonnet | $60.00 | Premium quality |

## Recommendations by Use Case

### Job Hunting (Need 10-25 applications)
**Recommended: GPT-4o (real-time)** or **Claude Sonnet**
- Cost: $4-15/month
- Real-time processing for urgent applications
- High quality for important applications

### Active Search (25-50 applications)
**Recommended: GPT-4o (batch)** or **GPT-4o-mini (real-time)**
- Cost: $2-11/month
- Good balance of cost and quality
- Mix batch for non-urgent, real-time for urgent

### High Volume (50+ applications)
**Recommended: GPT-4o-mini (batch)**
- Cost: $2-4/month for 50-100 jobs
- Maximum cost efficiency
- Still good quality output

### Maximum Quality (Budget not a concern)
**Recommended: Claude Sonnet 3.5** or **GPT-4o**
- Best reasoning and writing quality
- Real-time processing
- Worth it for dream jobs

## Configuration Examples

### Most Cost-Effective Setup

```yaml
api:
  provider: openai
  openai_key: your-key-here
  openai_model: gpt-4o-mini
  use_batch: true  # 50% savings
```

**Cost: ~$0.04 per job**

### Balanced Setup

```yaml
api:
  provider: openai
  openai_key: your-key-here
  openai_model: gpt-4o
  use_batch: true  # For non-urgent jobs
```

**Cost: ~$0.21 per job**

### Premium Quality Setup

```yaml
api:
  provider: anthropic
  anthropic_key: your-key-here
```

**Cost: ~$0.60 per job**

### Hybrid Approach (Recommended)

Use two configs:
1. **Batch config** for building your application queue
2. **Real-time config** for urgent opportunities

```bash
# Build queue overnight with batch processing
python main.py --config config_batch.yml --monitor

# Process urgent job immediately
python main.py --config config_realtime.yml --email-id <id>
```

## Cost Calculator

Use the built-in cost calculator:

```bash
# Show comparison table
python src/cost_tracker.py --compare

# Get recommendation based on budget
python src/cost_tracker.py --budget 10 --applications 25
```

Example output:
```
Recommended: openai gpt-4o (batch) at $0.210 per application
Estimated monthly cost: $5.25
```

## Free Tier / Credits

### OpenAI
- New accounts: $5 free trial credits
- Covers ~60-125 applications (depending on model)
- Expires after 3 months

### Anthropic
- New accounts: Sometimes offers promotional credits
- Check console.anthropic.com for current offers

## Tips to Minimize Costs

1. **Use batch API** when possible (50% savings)
2. **Start with GPT-4o-mini** - test quality before upgrading
3. **Set spending limits** in provider console
4. **Process multiple jobs at once** to amortize startup costs
5. **Use real-time only for urgent** applications
6. **Monitor costs** with the cost tracker utility

## Cost Tracking

The system automatically logs costs:

```
INFO - API cost (batch): $0.0421 (input: 2134, output: 987)
```

Check your logs to track actual spending:
```bash
grep "API cost" logs/job_automation.log | tail -20
```

## ROI Analysis

Time saved per application:
- Manual resume customization: 1-2 hours
- Manual cover letter: 30-60 minutes
- Gap analysis: 30 minutes
- **Total: 2-3.5 hours per application**

At $0.04-0.60 per application, you're paying:
- **$0.01-0.20 per hour of work saved**

Even at premium pricing, this is extremely cost-effective compared to your time value.

## Questions?

Run the cost comparison tool:
```bash
python src/cost_tracker.py --compare
```

Or check your expected costs:
```bash
python src/cost_tracker.py --budget 15 --applications 25
```
