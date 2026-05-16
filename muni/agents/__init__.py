"""Agent runtime and municipal intelligence agents."""

from muni.agents.anomaly import AnomalyDetectionAgent
from muni.agents.classification import DocumentClassificationAgent
from muni.agents.discovery import DocumentDiscoveryAgent
from muni.agents.extraction import OCRExtractionAgent
from muni.agents.fiscal_analysis import FiscalAnalysisAgent
from muni.agents.governance import GovernanceMappingAgent
from muni.agents.ontology import OntologyNormalizationAgent
from muni.agents.spatial import SpatialIntelligenceAgent
from muni.agents.visualization import VisualizationAgent
from muni.agents.narrative import NarrativeSynthesisAgent


DEFAULT_AGENT_CLASSES = [
    DocumentDiscoveryAgent,
    DocumentClassificationAgent,
    OCRExtractionAgent,
    OntologyNormalizationAgent,
    FiscalAnalysisAgent,
    GovernanceMappingAgent,
    SpatialIntelligenceAgent,
    AnomalyDetectionAgent,
    VisualizationAgent,
    NarrativeSynthesisAgent,
]

