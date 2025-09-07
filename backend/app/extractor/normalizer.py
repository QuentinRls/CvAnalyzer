import re
from datetime import datetime
from dateutil.parser import parse as parse_date
from typing import List, Optional

from ..schemas import Extracted, Language
from ..utils import logger


def normalize_extracted_data(data: Extracted) -> Extracted:
    """
    Normalize extracted data for consistency
    
    Args:
        data: Raw extracted data
        
    Returns:
        Normalized extracted data
    """
    logger.info("Normalizing extracted data")
    
    # Normalize dates in projects
    for project in data.projects:
        project.date_range = normalize_date_range(project.date_range)
    
    # Normalize language levels
    for language in data.languages:
        language.level = normalize_language_level(language.level)
    
    # Calculate years of experience if not set or seems wrong
    if data.candidate.years_experience <= 0:
        calculated_years = calculate_years_experience(data.experiences_key)
        if calculated_years > 0:
            data.candidate.years_experience = calculated_years
            logger.info(f"Calculated years of experience: {calculated_years}")
    
    # Clean and deduplicate skills
    data.skills = normalize_skills(data.skills)
    
    return data


def normalize_date_range(date_range: str) -> str:
    """
    Normalize date range to consistent format
    
    Args:
        date_range: Raw date range string
        
    Returns:
        Normalized date range in format "YYYY-MM → YYYY-MM" or original if cannot parse
    """
    if not date_range:
        return ""
    
    try:
        # Common patterns
        patterns = [
            r'(\d{4})-(\d{2})\s*[→-]\s*(\d{4})-(\d{2})',  # 2022-03 → 2023-02
            r'(\d{2})/(\d{4})\s*[→-]\s*(\d{2})/(\d{4})',  # 03/2022 → 02/2023
            r'(\w+)\s+(\d{4})\s*[→-]\s*(\w+)\s+(\d{4})',  # mars 2022 → février 2023
            r'(\d{4})\s*[→-]\s*(\d{4})',  # 2022 → 2023
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_range, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                if len(groups) == 4:
                    if pattern == patterns[0]:  # Already in correct format
                        return f"{groups[0]}-{groups[1]} → {groups[2]}-{groups[3]}"
                    elif pattern == patterns[1]:  # MM/YYYY format
                        return f"{groups[1]}-{groups[0].zfill(2)} → {groups[3]}-{groups[2].zfill(2)}"
                    elif pattern == patterns[2]:  # Month name format
                        start_month = parse_month_name(groups[0])
                        end_month = parse_month_name(groups[2])
                        if start_month and end_month:
                            return f"{groups[1]}-{start_month:02d} → {groups[3]}-{end_month:02d}"
                elif len(groups) == 2:  # Year only
                    return f"{groups[0]}-01 → {groups[1]}-12"
        
        # Try to parse with dateutil as fallback
        parts = re.split(r'[→-]|to|jusqu\'?à', date_range, 2)
        if len(parts) == 2:
            try:
                start = parse_date(parts[0].strip())
                end = parse_date(parts[1].strip())
                return f"{start.year}-{start.month:02d} → {end.year}-{end.month:02d}"
            except:
                pass
    
    except Exception as e:
        logger.warning(f"Could not normalize date range '{date_range}': {e}")
    
    return date_range


def parse_month_name(month_str: str) -> Optional[int]:
    """Parse French/English month names to month number"""
    month_map = {
        'janvier': 1, 'january': 1, 'jan': 1,
        'février': 2, 'fevrier': 2, 'february': 2, 'feb': 2,
        'mars': 3, 'march': 3, 'mar': 3,
        'avril': 4, 'april': 4, 'apr': 4,
        'mai': 5, 'may': 5,
        'juin': 6, 'june': 6, 'jun': 6,
        'juillet': 7, 'july': 7, 'jul': 7,
        'août': 8, 'aout': 8, 'august': 8, 'aug': 8,
        'septembre': 9, 'september': 9, 'sep': 9, 'sept': 9,
        'octobre': 10, 'october': 10, 'oct': 10,
        'novembre': 11, 'november': 11, 'nov': 11,
        'décembre': 12, 'decembre': 12, 'december': 12, 'dec': 12
    }
    
    return month_map.get(month_str.lower().strip())


def normalize_language_level(level: str) -> str:
    """
    Normalize language level to standard values
    
    Args:
        level: Raw level string
        
    Returns:
        Standardized level: debutant, intermediaire, courant, bilingue
    """
    level_lower = level.lower().strip()
    
    # Direct matches
    if level_lower in ['debutant', 'intermediaire', 'courant', 'bilingue']:
        return level_lower
    
    # Mapping from various formats
    level_map = {
        'débutant': 'debutant',
        'beginner': 'debutant',
        'basic': 'debutant',
        'a1': 'debutant',
        'a2': 'debutant',
        
        'intermédiaire': 'intermediaire',
        'intermediate': 'intermediaire',
        'b1': 'intermediaire',
        'b2': 'intermediaire',
        
        'avancé': 'courant',
        'avance': 'courant',
        'advanced': 'courant',
        'fluent': 'courant',
        'c1': 'courant',
        
        'natif': 'bilingue',
        'native': 'bilingue',
        'mothertounge': 'bilingue',
        'langue maternelle': 'bilingue',
        'c2': 'bilingue',
    }
    
    return level_map.get(level_lower, 'intermediaire')  # Default to intermediaire


def calculate_years_experience(experiences: List) -> int:
    """
    Calculate total years of experience from experience list
    
    Args:
        experiences: List of experience entries with duration_text
        
    Returns:
        Total years of experience (rounded)
    """
    total_months = 0
    
    for exp in experiences:
        duration = exp.duration_text
        if not duration:
            continue
        
        # Extract duration in various formats
        months = extract_duration_months(duration)
        total_months += months
    
    # Convert to years and round
    years = round(total_months / 12)
    return max(0, years)


def extract_duration_months(duration_text: str) -> int:
    """Extract duration in months from text"""
    if not duration_text:
        return 0
    
    text = duration_text.lower()
    months = 0
    
    # Look for year patterns
    year_patterns = [
        r'(\d+)\s*an[s]?',
        r'(\d+)\s*year[s]?',
        r'(\d+)\s*yr[s]?'
    ]
    
    for pattern in year_patterns:
        match = re.search(pattern, text)
        if match:
            months += int(match.group(1)) * 12
    
    # Look for month patterns
    month_patterns = [
        r'(\d+)\s*mois',
        r'(\d+)\s*month[s]?',
        r'(\d+)\s*mo[s]?'
    ]
    
    for pattern in month_patterns:
        match = re.search(pattern, text)
        if match:
            months += int(match.group(1))
    
    # If no explicit duration found, try to parse date ranges
    if months == 0:
        months = estimate_months_from_dates(duration_text)
    
    return months


def estimate_months_from_dates(text: str) -> int:
    """Estimate months from date range text"""
    try:
        # Try to find date patterns
        date_parts = re.split(r'[→-]|to|jusqu\'?à', text)
        if len(date_parts) == 2:
            start_str = date_parts[0].strip()
            end_str = date_parts[1].strip()
            
            # Handle "present", "current", etc.
            if any(word in end_str.lower() for word in ['present', 'current', 'actuel', 'aujourd\'hui']):
                end_date = datetime.now()
            else:
                try:
                    end_date = parse_date(end_str)
                except:
                    return 0
            
            try:
                start_date = parse_date(start_str)
                months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                return max(0, months)
            except:
                pass
    except:
        pass
    
    return 0


def normalize_skills(skills) -> any:
    """
    Clean and deduplicate skills
    
    Args:
        skills: Skills object
        
    Returns:
        Cleaned skills object
    """
    # Clean technical skills and convert arrays to comma-separated strings for frontend compatibility
    for category in ['language_framework', 'ci_cd', 'state_management', 'tests', 
                     'tools', 'databases_big_data', 'analytics_visualization', 
                     'collaboration', 'ux_ui']:
        skill_list = getattr(skills.technical, category, [])
        cleaned = clean_skill_list(skill_list)
        # Convert array to comma-separated string for frontend compatibility
        skills_string = ", ".join(cleaned) if cleaned else ""
        setattr(skills.technical, category, skills_string)
    
    # Clean functional and management skills (keep as arrays)
    skills.functional = clean_skill_list(skills.functional)
    skills.management = clean_skill_list(skills.management)
    
    return skills


def clean_skill_list(skills: List[str]) -> List[str]:
    """Clean and deduplicate a list of skills"""
    if not skills:
        return []
    
    cleaned = []
    seen = set()
    
    for skill in skills:
        if not skill or not skill.strip():
            continue
        
        # Clean the skill
        clean_skill = skill.strip().title()
        
        # Deduplicate (case insensitive)
        if clean_skill.lower() not in seen:
            cleaned.append(clean_skill)
            seen.add(clean_skill.lower())
    
    return cleaned
