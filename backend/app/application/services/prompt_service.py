"""
Prompt Management Service (V3.0).

Handles database-stored Jinja2 prompt templates with versioning.
"""

import logging
from typing import Dict, Any, Optional
from jinja2 import Environment, DictLoader, TemplateNotFound, TemplateSyntaxError
import sqlite3
import json

from app.domain.prompts.template_seeds import get_template_seeds

logger = logging.getLogger(__name__)


class PromptService:
    """
    Service for managing and rendering Jinja2 prompt templates.
    
    Templates are stored in the database with versioning support.
    """
    
    def __init__(self, db_path: str = "jobwise.db"):
        """
        Initialize prompt service.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.env: Optional[Environment] = None
        self._load_templates()
    
    def _load_templates(self):
        """Load templates from database into Jinja2 Environment."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Fetch all active templates
            cursor.execute("""
                SELECT template_name, template_content
                FROM prompt_templates
                WHERE is_active = 1
                ORDER BY template_name, version DESC
            """)
            
            templates = {}
            seen_names = set()
            
            for name, content in cursor.fetchall():
                # Only take the first (highest version) for each name
                if name not in seen_names:
                    templates[name] = content
                    seen_names.add(name)
            
            conn.close()
            
            if not templates:
                logger.warning("No active templates found in database")
                templates = {}
            
            # Create Jinja2 environment with DictLoader
            self.env = Environment(
                loader=DictLoader(templates),
                autoescape=False,  # Don't escape for LLM prompts
                trim_blocks=True,
                lstrip_blocks=True
            )
            
            logger.info(f"Loaded {len(templates)} prompt templates: {list(templates.keys())}")
        
        except sqlite3.Error as e:
            logger.error(f"Failed to load templates from database: {e}")
            # Create empty environment as fallback
            self.env = Environment(loader=DictLoader({}))
    
    def render(
        self,
        template_name: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        Render a prompt template with variables.
        
        Args:
            template_name: Name of the template to render
            variables: Dictionary of variables to inject
            
        Returns:
            Rendered prompt text
            
        Raises:
            ValueError: Template not found or rendering failed
        """
        if not self.env:
            raise ValueError("Prompt environment not initialized")
        
        try:
            template = self.env.get_template(template_name)
            rendered = template.render(**variables)
            
            logger.debug(f"Rendered template '{template_name}' with {len(variables)} variables")
            return rendered.strip()
        
        except TemplateNotFound:
            logger.error(f"Template not found: {template_name}")
            raise ValueError(f"Template '{template_name}' not found")
        
        except TemplateSyntaxError as e:
            logger.error(f"Template syntax error in '{template_name}': {e}")
            raise ValueError(f"Template syntax error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Failed to render template '{template_name}': {e}")
            raise ValueError(f"Rendering failed: {str(e)}")
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata about a template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template metadata dict or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, version, required_variables, optional_variables,
                       description, expected_output_format, estimated_tokens
                FROM prompt_templates
                WHERE template_name = ? AND is_active = 1
                ORDER BY version DESC
                LIMIT 1
            """, (template_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            return {
                "id": row[0],
                "name": template_name,
                "version": row[1],
                "required_variables": json.loads(row[2]) if row[2] else [],
                "optional_variables": json.loads(row[3]) if row[3] else {},
                "description": row[4],
                "expected_output_format": row[5],
                "estimated_tokens": row[6]
            }
        
        except sqlite3.Error as e:
            logger.error(f"Failed to get template info for '{template_name}': {e}")
            return None
    
    def reload_templates(self):
        """Reload templates from database."""
        logger.info("Reloading templates from database")
        self._load_templates()
    
    @staticmethod
    def seed_templates(db_path: str = "jobwise.db") -> int:
        """
        Seed initial prompt templates into database.
        
        Args:
            db_path: Path to SQLite database
            
        Returns:
            Number of templates seeded
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            templates = get_template_seeds()
            seeded_count = 0
            
            for template in templates:
                # Check if template already exists
                cursor.execute("""
                    SELECT id FROM prompt_templates
                    WHERE template_name = ? AND version = ?
                """, (template["template_name"], template["version"]))
                
                if cursor.fetchone():
                    logger.info(f"Template '{template['template_name']}' v{template['version']} already exists, skipping")
                    continue
                
                # Insert new template
                cursor.execute("""
                    INSERT INTO prompt_templates (
                        id, template_name, version, is_active, template_content,
                        required_variables, optional_variables, description,
                        expected_output_format, estimated_tokens, ab_test_group,
                        performance_metrics, deprecated_at, superseded_by_template_id,
                        created_at, updated_at, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    template["id"],
                    template["template_name"],
                    template["version"],
                    template["is_active"],
                    template["template_content"],
                    json.dumps(template["required_variables"]),
                    json.dumps(template["optional_variables"]),
                    template["description"],
                    template["expected_output_format"],
                    template["estimated_tokens"],
                    template["ab_test_group"],
                    json.dumps(template["performance_metrics"]),
                    template["deprecated_at"],
                    template["superseded_by_template_id"],
                    template["created_at"],
                    template["updated_at"],
                    template["created_by"]
                ))
                
                seeded_count += 1
                logger.info(f"Seeded template: {template['template_name']} v{template['version']}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Successfully seeded {seeded_count} prompt templates")
            return seeded_count
        
        except sqlite3.Error as e:
            logger.error(f"Failed to seed templates: {e}")
            raise


# FastAPI dependency for injection
def get_prompt_service(db_path: str = "jobwise.db") -> PromptService:
    """
    FastAPI dependency for PromptService injection.
    
    Usage:
        @app.post("/endpoint")
        async def endpoint(prompts: PromptService = Depends(get_prompt_service)):
            ...
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        PromptService instance
    """
    return PromptService(db_path=db_path)
