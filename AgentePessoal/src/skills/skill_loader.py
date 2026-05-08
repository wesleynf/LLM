"""
skill_loader.py — Carrega habilidades dinamicamente.
"""
import os
import yaml
import logging
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)

@dataclass
class SkillMetadata:
    name: str
    description: str

@dataclass
class Skill:
    metadata: SkillMetadata
    content: str
    path: str

class SkillLoader:
    """
    Carrega skills de arquivos SKILL.md com frontmatter YAML.
    """

    def __init__(self, skills_dir: str = ".agents/skills"):
        self.skills_dir = skills_dir

    def load_active_skills(self) -> List[Skill]:
        skills = []
        if not os.path.exists(self.skills_dir):
            logger.warning(f"Diretório de skills não encontrado: {self.skills_dir}")
            return []

        for root, dirs, files in os.walk(self.skills_dir):
            if "SKILL.md" in files:
                skill_path = os.path.join(root, "SKILL.md")
                skill = self._parse_skill_file(skill_path)
                if skill:
                    skills.append(skill)
        
        return skills

    def _parse_skill_file(self, path: str) -> Optional[Skill]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Separar frontmatter (--- YAML ---) do conteúdo MD
            parts = content.split('---', 2)
            if len(parts) < 3:
                return None
            
            metadata_yaml = yaml.safe_load(parts[1])
            metadata = SkillMetadata(
                name=metadata_yaml.get('name', 'unnamed'),
                description=metadata_yaml.get('description', '')
            )
            
            return Skill(
                metadata=metadata,
                content=parts[2].strip(),
                path=path
            )
        except Exception as e:
            logger.error(f"Erro ao carregar skill {path}: {e}")
            return None
