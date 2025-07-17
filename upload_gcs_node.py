import os
import tempfile
import uuid
from PIL import Image
from google.cloud import storage

class UploadImageToGCS:
    """
    A ComfyUI node that uploads an image to Google Cloud Storage
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "bucket_name": ("STRING", {"default": "my-bucket"}),
                "service_account_path": ("STRING", {"default": "service-account.json"})
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("public_url",)
    FUNCTION = "upload_to_gcs"
    CATEGORY = "🍿PapcornsNodes/gcs"
    
    def upload_to_gcs(self, image, bucket_name, service_account_path):
        # Create a temporary file to save the image
        temp_dir = tempfile.gettempdir()
        random_filename = f"{uuid.uuid4()}.png"
        temp_file_path = os.path.join(temp_dir, random_filename)
        
        # Convert the image tensor to a PIL image and save it
        # ComfyUI images are in format [batch, height, width, channel] and normalized
        i = 255. * image.cpu().numpy()
        img = Image.fromarray(i.astype('uint8')[0])
        img.save(temp_file_path)
        
        try:
            # Set the environment variable for GCP authentication
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path
            
            # Initialize the storage client
            storage_client = storage.Client()
            
            # Get the bucket
            bucket = storage_client.bucket(bucket_name)
            
            # Upload the file to GCS
            blob = bucket.blob(random_filename)
            blob.upload_from_filename(temp_file_path)
            
            # Make the blob publicly accessible
            blob.make_public()
            
            # Get the public URL
            public_url = blob.public_url
            
            # Clean up the temporary file
            os.remove(temp_file_path)
            
            return (public_url,)
            
        except Exception as e:
            # Clean up the temporary file in case of an error
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            # Return error message as URL
            error_message = f"Error uploading to GCS: {str(e)}"
            print(error_message)
            return (error_message,)

