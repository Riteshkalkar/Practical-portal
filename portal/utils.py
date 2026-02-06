import os
from django.conf import settings
from urllib.parse import quote

def get_google_docs_viewer_url(file_url):
    """
    Generate Google Docs viewer URL for file preview
    """
    if not file_url:
        return None
    
    try:
        # Ensure we have a full URL
        if file_url.startswith('/'):
            # If it's a relative URL, make it absolute
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            file_url = f"{base_url}{file_url}"
        
        # Google Docs viewer URL
        google_viewer_url = f"https://docs.google.com/gview?url={quote(file_url)}&embedded=true"
        return google_viewer_url
    except Exception as e:
        print(f"Error generating Google Docs viewer URL: {e}")
        return None

def get_file_extension(file_path):
    """
    Get file extension from file path
    """
    if not file_path:
        return None
    return os.path.splitext(str(file_path))[1].lower()

def is_viewable_file(file_path):
    """
    Check if file can be viewed in Google Docs viewer
    """
    viewable_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', ]
    extension = get_file_extension(file_path)
    return extension in viewable_extensions

def get_file_icon(file_path):
    """
    Get appropriate icon for file type
    """
    extension = get_file_extension(file_path)
    
    icon_map = {
        '.pdf': 'fas fa-file-pdf',
        '.doc': 'fas fa-file-word',
        '.docx': 'fas fa-file-word',
        '.ppt': 'fas fa-file-powerpoint',
        '.pptx': 'fas fa-file-powerpoint',
       
    }
    
    return icon_map.get(extension, 'fas fa-file')
