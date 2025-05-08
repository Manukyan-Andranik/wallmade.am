import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def upload_to_cloudinary(image_path, folder_name=None):
    """
    Upload an image to Cloudinary in a specified folder.
    
    Args:
        image_path (str): Path to the local image file
        folder_name (str, optional): Folder name in Cloudinary. Defaults to None.
    
    Returns:
        dict: Upload response from Cloudinary
    """
    try:
        # Configure Cloudinary with your credentials
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET'),
            secure=True
        )
        
        # Prepare upload options
        upload_options = {
            'resource_type': 'image',
            'quality_analysis': True
        }
        
        # Add folder if specified
        if folder_name:
            upload_options['folder'] = folder_name
        
        # Upload the image
        result = cloudinary.uploader.upload(image_path, **upload_options)
        
        print(f"Successfully uploaded {image_path} to Cloudinary!")
        print(f"Public URL: {result['secure_url']}")
        print(f"Public ID: {result['public_id']}")
        
        return result
        
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        return None

# def main():
#     print("Cloudinary Image Uploader")
#     print("------------------------")
    
#     # Get user input
#     image_path = "static/images/employees/seo.png"
#     folder_name = "Products"
    
#     # Validate file exists
#     if not os.path.isfile(image_path):
#         print("Error: The specified file does not exist.")
#         return
    
#     # Upload the image
#     upload_to_cloudinary(image_path, folder_name)


import cloudinary
import cloudinary.api
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def get_images_from_folder(folder_name, max_results=100):
    """
    Retrieve all images from a specified folder in Cloudinary.
    
    Args:
        folder_name (str): Name of the folder in Cloudinary
        max_results (int): Maximum number of results to return (default 100)
    
    Returns:
        list: List of image resources with their details
    """
    try:
        # Configure Cloudinary with your credentials
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET'),
            secure=True
        )
        
        # Make sure folder name ends with a slash
        if not folder_name.endswith('/'):
            folder_name += '/'
        
        # Get resources from the specified folder
        resources = cloudinary.api.resources(
            type='upload',
            prefix=folder_name,
            max_results=max_results,
            resource_type='image'
        )
        
        # Filter to only include items in the exact folder (not subfolders)
        images = [
            resource for resource in resources.get('resources', [])
            if resource['public_id'].startswith(folder_name) and 
               '/' not in resource['public_id'][len(folder_name):]
        ]
        
        print(f"Found {len(images)} images in folder '{folder_name}'")
        return images
        
    except Exception as e:
        print(f"Error retrieving images: {str(e)}")
        return []

def display_image_info(images):
    """
    Display information about the retrieved images.
    
    Args:
        images (list): List of image resources from Cloudinary
    """
    if not images:
        print("No images found.")
        return
    
    print("\nImage Details:")
    print("-------------")
    for idx, image in enumerate(images, 1):
        print(f"{idx}. {image['public_id']}")
        print(f"   URL: {image['secure_url']}")
        print(f"   Format: {image['format']}")
        print(f"   Size: {image['bytes']} bytes")
        print(f"   Dimensions: {image['width']}x{image['height']}")
        print(f"   Created: {image['created_at']}")
        print()

def main():
    print("Cloudinary Folder Image Retriever")
    print("--------------------------------")
    
    # Get user input
    folder_name = "Products"
    
    if not folder_name:
        print("Error: Folder name cannot be empty.")
        return
    
    # Get images from folder
    images = get_images_from_folder(folder_name)
    
    # Display the results
    display_image_info(images)


if __name__ == "__main__":
    main()