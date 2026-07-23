# CHITTI: Required APIs & Integrations for "Full Throttle"

CHITTI is designed as a **local-first** AI Desktop Companion. Its core intelligence (Wake Word, Speech-to-Text, Text-to-Speech, Reasoning LLMs, and Vision) runs entirely locally on your hardware. 

However, to operate at **full throttle** and unleash the true power of its Productivity, Developer, and Research Suites, CHITTI needs secure access to your personal digital ecosystem. 

Below is the definitive list of API keys and OAuth integrations required for CHITTI to unlock all of its features.

---

## 1. Productivity Suite (Email, Calendar, Documents)
To power the **Smart Email Assistant**, **Meeting Companion**, and **Daily Overview**, CHITTI needs to read and write to your schedule and inbox.

* **Google Workspace / Microsoft 365 (OAuth)**
  * **Required For**: Syncing emails, managing calendar events, extracting meeting links, and drafting replies.
  * *Note: Instead of raw API keys, these usually require standard OAuth 2.0 authentication flows granted locally.*

## 2. Web Search & Research (Research Companion)
While CHITTI uses Playwright/Crawl4AI to read websites locally, it needs a search engine API to discover those websites in the first place when running the **Research Companion**.

* **Tavily API** (Recommended) or **Bing Web Search API** / **Google Custom Search API**
  * **Required For**: Semantic web search, finding live sources, aggregating news for the Morning Briefing, and verifying claims.

## 3. Developer Suite (Resume Coding, Activity Tracker)
To function as an effective coding companion, CHITTI needs to interact with your version control systems seamlessly.

* **GitHub / GitLab Personal Access Token (PAT)**
  * **Required For**: Reviewing uncommitted changes, reading issue trackers, automatically summarizing pull requests, and generating `GitRepositoryResource` cards.

## 4. Environment & Context (Daily Overview)
To contextualize your day, CHITTI relies on real-world environment data.

* **OpenWeatherMap API** (or similar)
  * **Required For**: Local weather context injected into the Daily Overview and Morning Briefing.

---

## 5. Optional Cloud AI (For "Turbo Mode")
CHITTI uses local GGUF models (Qwen2.5-1.5B / Sarvam-2B) by default. However, the `DecisionEngine` supports seamless swapping to frontier cloud models if you require heavy reasoning, complex coding, or massive context windows that exceed your local RAM.

* **OpenAI API Key** (GPT-4o)
* **Anthropic API Key** (Claude 3.5 Sonnet)
* **Google Gemini API Key** (Gemini 1.5 Pro)
  * **Required For**: Opting into cloud execution for complex reasoning tasks, extremely fast TTS generation (e.g., OpenAI TTS), or advanced cloud-based vision tasks.

---

## Summary Checklist for Maximum Capability

- [ ] Google/Microsoft OAuth (Calendar, Email, Contacts)
- [ ] Tavily / Bing Search API Key (Web Search)
- [ ] GitHub Personal Access Token (Git context)
- [ ] OpenWeatherMap API Key (Morning Briefing)
- [ ] *Optional:* OpenAI / Anthropic Key (For frontier AI reasoning)
