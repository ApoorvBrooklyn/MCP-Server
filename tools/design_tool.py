"""
Design Tool - Create quote graphics using the free Figma API
"""

import os
import requests
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Figma API configuration
FIGMA_API_KEY = os.getenv('FIGMA_API_KEY')
FIGMA_FILE_ID = os.getenv('FIGMA_FILE_ID')
FIGMA_BASE_URL = "https://api.figma.com/v1"


def create_quote_graphic(quote_text: str, template_node_id: str = None) -> str:
    """
    Create a quote graphic using Figma API
    
    Args:
        quote_text (str): Quote text to display in the graphic
        template_node_id (str): Specific node ID to update (optional)
        
    Returns:
        str: URL or path to the generated graphic
        
    Raises:
        Exception: If graphic creation fails or API keys are missing
    """
    try:
        if not FIGMA_API_KEY or not FIGMA_FILE_ID:
            raise Exception("FIGMA_API_KEY and FIGMA_FILE_ID must be set in .env file")
        
        # Get file information
        file_info = get_figma_file_info()
        
        # Find text nodes to update
        text_nodes = find_text_nodes(file_info, template_node_id)
        
        if not text_nodes:
            raise Exception("No suitable text nodes found in Figma file")
        
        # Update the first suitable text node with our quote
        node_to_update = text_nodes[0]
        node_id = node_to_update['id']
        
        # Update the text content
        success = update_text_node(node_id, quote_text)
        
        if not success:
            raise Exception("Failed to update text in Figma")
        
        # Export the updated frame as an image
        image_url = export_node_as_image(node_id)
        
        # Download and save the image locally
        local_path = download_image(image_url, quote_text)
        
        print(f"Quote graphic created successfully: {local_path}")
        return local_path
        
    except Exception as e:
        raise Exception(f"Failed to create quote graphic: {str(e)}")


def get_figma_file_info() -> Dict[str, Any]:
    """
    Get Figma file information and structure
    
    Returns:
        Dict: File information including nodes
    """
    try:
        headers = {
            'X-Figma-Token': FIGMA_API_KEY
        }
        
        url = f"{FIGMA_BASE_URL}/files/{FIGMA_FILE_ID}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Figma API error: {response.status_code} - {response.text}")
        
        return response.json()
        
    except Exception as e:
        raise Exception(f"Failed to get Figma file info: {str(e)}")


def find_text_nodes(file_info: Dict[str, Any], specific_node_id: str = None) -> list:
    """
    Find text nodes in the Figma file that can be updated
    
    Args:
        file_info (Dict): Figma file information
        specific_node_id (str): Specific node ID to look for
        
    Returns:
        list: List of text nodes that can be updated
    """
    try:
        text_nodes = []
        
        def search_nodes(nodes):
            for node in nodes:
                if node.get('type') == 'TEXT':
                    # Check if this is a text node we can update
                    if specific_node_id is None or node['id'] == specific_node_id:
                        text_nodes.append(node)
                
                # Recursively search child nodes
                if 'children' in node:
                    search_nodes(node['children'])
        
        # Search through all pages
        for page in file_info.get('document', {}).get('children', []):
            search_nodes(page.get('children', []))
        
        return text_nodes
        
    except Exception as e:
        print(f"Warning: Could not find text nodes: {e}")
        return []


def update_text_node(node_id: str, new_text: str) -> bool:
    """
    Update a text node with new content
    
    Args:
        node_id (str): ID of the text node to update
        new_text (str): New text content
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        headers = {
            'X-Figma-Token': FIGMA_API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Prepare the update payload
        payload = {
            "document": {
                "children": [
                    {
                        "id": node_id,
                        "characters": new_text
                    }
                ]
            }
        }
        
        url = f"{FIGMA_BASE_URL}/files/{FIGMA_FILE_ID}/nodes"
        response = requests.post(url, headers=headers, json=payload)
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Warning: Could not update text node: {e}")
        return False


def export_node_as_image(node_id: str, format: str = "PNG", scale: int = 2) -> str:
    """
    Export a node as an image
    
    Args:
        node_id (str): ID of the node to export
        format (str): Image format (PNG, JPG, SVG)
        scale (int): Scale factor for the image
        
    Returns:
        str: URL to the exported image
    """
    try:
        headers = {
            'X-Figma-Token': FIGMA_API_KEY
        }
        
        params = {
            'ids': node_id,
            'format': format,
            'scale': scale
        }
        
        url = f"{FIGMA_BASE_URL}/images/{FIGMA_FILE_ID}"
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Export failed: {response.status_code} - {response.text}")
        
        data = response.json()
        return data['images'][node_id]
        
    except Exception as e:
        raise Exception(f"Failed to export node as image: {str(e)}")


def download_image(image_url: str, quote_text: str) -> str:
    """
    Download image from URL and save locally
    
    Args:
        image_url (str): URL of the image to download
        quote_text (str): Quote text for filename
        
    Returns:
        str: Local path to the downloaded image
    """
    try:
        # Create output directory
        output_dir = Path("generated_graphics")
        output_dir.mkdir(exist_ok=True)
        
        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Create filename from quote
        safe_filename = "".join(c for c in quote_text if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename[:50]  # Limit length
        
        import time
        timestamp = int(time.time())
        filename = f"quote_{safe_filename}_{timestamp}.png"
        file_path = output_dir / filename
        
        # Save the image
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        return str(file_path)
        
    except Exception as e:
        raise Exception(f"Failed to download image: {str(e)}")


def create_quote_variations(quote_text: str, styles: list = None) -> Dict[str, str]:
    """
    Create multiple quote graphic variations
    
    Args:
        quote_text (str): Quote text to display
        styles (list): List of style variations to create
        
    Returns:
        Dict: Dictionary mapping style names to file paths
    """
    try:
        if styles is None:
            styles = ["default", "bold", "minimal", "colorful"]
        
        results = {}
        
        for style in styles:
            try:
                # This would need different Figma templates or nodes for each style
                # For now, we'll create the same graphic with different filenames
                graphic_path = create_quote_graphic(quote_text)
                
                # Rename to include style
                style_path = graphic_path.replace(".png", f"_{style}.png")
                os.rename(graphic_path, style_path)
                
                results[style] = style_path
                
            except Exception as e:
                print(f"Failed to create {style} variation: {e}")
                continue
        
        return results
        
    except Exception as e:
        raise Exception(f"Failed to create quote variations: {str(e)}")


def optimize_quote_for_design(quote_text: str, max_length: int = 100) -> str:
    """
    Optimize quote text for graphic design
    
    Args:
        quote_text (str): Original quote text
        max_length (int): Maximum character length
        
    Returns:
        str: Optimized quote text
    """
    try:
        # Truncate if too long
        if len(quote_text) > max_length:
            quote_text = quote_text[:max_length-3] + "..."
        
        # Add line breaks for better readability
        words = quote_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= 40:  # Max 40 chars per line
                current_line += " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return "\n".join(lines)
        
    except Exception as e:
        print(f"Warning: Could not optimize quote: {e}")
        return quote_text


def get_figma_file_structure() -> Dict[str, Any]:
    """
    Get a simplified structure of the Figma file for debugging
    
    Returns:
        Dict: File structure with node information
    """
    try:
        file_info = get_figma_file_info()
        
        structure = {
            "pages": [],
            "text_nodes": []
        }
        
        for page in file_info.get('document', {}).get('children', []):
            page_info = {
                "name": page.get('name', 'Unknown'),
                "id": page.get('id', ''),
                "nodes": []
            }
            
            def extract_nodes(nodes, level=0):
                for node in nodes:
                    node_info = {
                        "name": node.get('name', 'Unknown'),
                        "id": node.get('id', ''),
                        "type": node.get('type', 'Unknown'),
                        "level": level
                    }
                    
                    if node.get('type') == 'TEXT':
                        structure["text_nodes"].append(node_info)
                    
                    page_info["nodes"].append(node_info)
                    
                    if 'children' in node:
                        extract_nodes(node['children'], level + 1)
            
            extract_nodes(page.get('children', []))
            structure["pages"].append(page_info)
        
        return structure
        
    except Exception as e:
        raise Exception(f"Failed to get file structure: {str(e)}")


if __name__ == "__main__":
    # Test the function
    test_quote = "This is a test quote for the design tool. It should create a beautiful graphic!"
    
    try:
        if not FIGMA_API_KEY or not FIGMA_FILE_ID:
            print("Please set FIGMA_API_KEY and FIGMA_FILE_ID in your .env file")
        else:
            graphic_path = create_quote_graphic(test_quote)
            print(f"Test successful: {graphic_path}")
    except Exception as e:
        print(f"Test failed: {e}")
