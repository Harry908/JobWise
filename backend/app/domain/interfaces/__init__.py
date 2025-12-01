"""Domain interfaces package."""

from .sample_repository_interface import SampleRepositoryInterface
from .writing_style_repository_interface import WritingStyleRepositoryInterface
from .ranking_repository_interface import RankingRepositoryInterface
from .generation_repository_interface import GenerationRepositoryInterface

__all__ = [
    "SampleRepositoryInterface",
    "WritingStyleRepositoryInterface",
    "RankingRepositoryInterface",
    "GenerationRepositoryInterface",
]
