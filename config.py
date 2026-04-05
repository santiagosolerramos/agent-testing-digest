import os
from pathlib import Path
from dotenv import load_dotenv

# Paths
ROOT_DIR = Path(__file__).parent

# Load .env relative to this file, not the CWD — so `python main.py` works from any directory
load_dotenv(ROOT_DIR / ".env")
REPORTS_DIR = ROOT_DIR / "reports"
SEEN_URLS_FILE = REPORTS_DIR / ".seen_urls.json"
PROMPTS_DIR = ROOT_DIR / "prompts"

# API keys
XAI_API_KEY: str = os.environ["XAI_API_KEY"]
GITHUB_TOKEN: str | None = os.getenv("GITHUB_TOKEN")
TAVILY_API_KEY: str | None = os.getenv("TAVILY_API_KEY")

# Search parameters
LOOKBACK_DAYS: int = int(os.getenv("LOOKBACK_DAYS", "1"))
MIN_SCORE: int = int(os.getenv("MIN_SCORE", "2"))
MAX_ITEMS_PER_SOURCE: int = int(os.getenv("MAX_ITEMS_PER_SOURCE", "30"))

# xAI model
XAI_BASE_URL = "https://api.x.ai/v1"
XAI_MODEL = "grok-3-mini"

# GitHub repos to monitor for releases
GITHUB_REPOS = [
    "brainlid/langchain",
    "confident-ai/deepeval",
    "explodinggradients/ragas",
    "langchain-ai/langsmith-sdk",
    "openai/evals",
    "microsoft/promptflow",
    "BerriAI/litellm",
    "anthropics/evals",
    "google/inspect_ai",
    "NVIDIA/nemo-guardrails",
    "uptrain-ai/uptrain",
    "trulens/trulens",
    "pydantic/pydantic-ai",
    "microsoft/autogen",
    "crewAIInc/crewAI",
]

# RSS feeds to monitor
RSS_FEEDS = [
    ("Anthropic Blog", "https://www.anthropic.com/rss.xml"),
    ("OpenAI Blog", "https://openai.com/blog/rss.xml"),
    ("Google DeepMind Blog", "https://deepmind.google/blog/rss.xml"),
    ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml"),
    ("LangChain Blog", "https://blog.langchain.dev/rss/"),
    ("Lilian Weng Blog", "https://lilianweng.github.io/index.xml"),
    ("Sebastian Raschka", "https://magazine.sebastianraschka.com/feed"),
    ("dev.to — llm", "https://dev.to/feed/tag/llm"),
    ("dev.to — agents", "https://dev.to/feed/tag/agents"),
    ("dev.to — llmops", "https://dev.to/feed/tag/llmops"),
    ("Braintrust Blog", "https://www.braintrust.dev/blog/rss.xml"),
    ("Humanloop Blog", "https://humanloop.com/blog/rss.xml"),
    # Google Alerts — agregar URLs cuando estén configuradas las alertas:
    # ("Google Alerts — agent evaluation", "https://www.google.com/alerts/feeds/ID/ID"),
    # ("Google Alerts — llm testing", "https://www.google.com/alerts/feeds/ID/ID"),
]

# Keywords for ranking — tuned to Connectly / Talk Framework context
HIGH_VALUE_KEYWORDS = [
    "agent eval",
    "agent evaluation",
    "llm eval",
    "llm evaluation",
    "agent testing",
    "synthetic user",
    "simulated user",
    "persona simulation",
    "conversational agent",
    "chatbot evaluation",
    "regression testing",
    "evals",
    "red teaming",
    "adversarial testing",
    "benchmark agent",
    "multi-turn",
    "dialogue evaluation",
    "automated testing",
    "test framework",
    "evaluation framework",
    "grounding",
    "faithfulness",
    "hallucination detection",
]

MEDIUM_VALUE_KEYWORDS = [
    "rag evaluation",
    "fine-tuning eval",
    "prompt testing",
    "tool use",
    "function calling",
    "whatsapp",
    "conversational ai",
    "llm benchmark",
    "model evaluation",
    "human feedback",
    "reinforcement learning",
    "reward model",
    "alignment",
]
