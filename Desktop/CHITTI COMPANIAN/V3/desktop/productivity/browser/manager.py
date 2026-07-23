import time
import uuid
from typing import List, Optional
from desktop.models.session import WorkSession
from desktop.models.browser import BrowserContext, BrowserTab, DomainCluster
from desktop.models.evidence import EvidenceSource, RedundantEvidence, ProviderEvidence, EvidenceDomain
from desktop.models.identity import UnknownIdentity
from desktop.productivity.browser.chrome_provider import ChromeProvider
from desktop.productivity.browser.edge_provider import EdgeProvider
from desktop.productivity.providers.base import ContextProvider, ProviderCapabilities

class BrowserManager(ContextProvider):
    """
    Manages Browser Providers and correlates SQLite URLs with Active Window timeline.
    """
    def __init__(self):
        self.providers = [ChromeProvider(), EdgeProvider()]
        
    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_realtime=True,
            supports_history=True,
            supports_restore=True,
            supports_statistics=True,
            supports_background_processing=True
        )
        
    @property
    def domain(self) -> EvidenceDomain:
        return EvidenceDomain.RESEARCH
        
    @property
    def name(self) -> str:
        return "browser"
        
    def build_evidence(self, session: WorkSession) -> ProviderEvidence:
        # Only process if we have browser hints in the session
        if not session.browser_title_hints:
            return ProviderEvidence()
            
        since_ts = session.start_time
        all_tabs = []
        primary_browser = "Unknown"
        
        # 1. Fetch from all providers
        for provider in self.providers:
            tabs = provider.extract_recent_history(since_ts)
            if tabs:
                primary_browser = provider.browser_name
                all_tabs.extend(tabs)
                
        if not all_tabs:
            return ProviderEvidence()
            
        # 2. Correlate with active_windows to find reading_duration and exact matches
        matched_tabs = []
        domains = set()
        total_reading_time = 0.0
        
        for i, window_event in enumerate(session.active_windows):
            ts, app, title = window_event
            is_browser = False
            for p in self.providers:
                if any(exe in app.lower() for exe in p.executable_names):
                    is_browser = True
                    break
                    
            if not is_browser:
                continue
                
            duration = 0.0
            if i + 1 < len(session.active_windows):
                duration = session.active_windows[i+1][0] - ts
            else:
                duration = time.time() - ts
                
            best_tab = None
            min_diff = 60.0
            
            for tab in all_tabs:
                diff = abs(tab.opened_at - ts)
                if diff < min_diff and (title.lower() in tab.title.lower() or tab.title.lower() in title.lower()):
                    min_diff = diff
                    best_tab = tab
                    
            if best_tab:
                enriched_tab = BrowserTab(
                    url=best_tab.url,
                    title=best_tab.title,
                    domain=best_tab.domain,
                    opened_at=ts,
                    closed_at=ts + duration,
                    reading_duration=duration
                )
                matched_tabs.append(enriched_tab)
                domains.add(enriched_tab.domain)
                total_reading_time += duration
                
        if not matched_tabs:
            return ProviderEvidence()
            
        # 3. Deterministic Clustering (Domain Clusters & Redundant Evidence)
        domain_clusters = {}
        redundancies = {}
        unique_urls = set()
        
        for tab in matched_tabs:
            source = EvidenceSource(
                source_id=f"browser_{uuid.uuid4().hex[:8]}",
                provider=primary_browser,
                timestamp=tab.opened_at,
                confidence=1.0,
                raw_reference=tab
            )
            
            # Domain Clustering
            if tab.domain not in domain_clusters:
                domain_clusters[tab.domain] = DomainCluster(
                    label=tab.domain, 
                    identity=UnknownIdentity(
                        id=f"url_{uuid.uuid5(uuid.NAMESPACE_URL, tab.domain).hex[:8]}",
                        type="UNKNOWN",
                        display_name=tab.domain,
                        canonical_path=tab.domain
                    ),
                    duration=0.0
                )
            cluster = domain_clusters[tab.domain]
            cluster.sources.append(source)
            cluster.duration += tab.reading_duration
            
            if not cluster.primary_tab or tab.reading_duration > cluster.primary_tab.reading_duration:
                cluster.primary_tab = tab
                
            # Redundant Evidence
            if tab.url not in redundancies:
                redundancies[tab.url] = RedundantEvidence(label=tab.url, count=0)
                unique_urls.add(tab.url)
                
            red_group = redundancies[tab.url]
            red_group.count += 1
            red_group.sources.append(source)
            
        actual_redundancies = [group for url, group in redundancies.items() if group.count > 1]
            
        # We also still construct the old BrowserContext if someone needs it, 
        # but for EpisodeBuilder we return ProviderEvidence.
        # Actually, let's just return ProviderEvidence.
        return ProviderEvidence(
            clusters=list(domain_clusters.values()),
            redundancies=actual_redundancies,
            statistics={
                "browser": primary_browser,
                "total_reading_time": total_reading_time,
                "total_tabs": len(matched_tabs),
                "unique_tabs": len(unique_urls)
            },
            metadata={
                "domains": list(domains)
            }
        )
