    """ This program takes a directory path of images and processes them for cull flags
    ********************************
    1. Take directory path for Smart Previews. DONE
    2. Recursively parse directory into List. DONE
    3. Convert DNG to JPG. DONE
    4. Resize images smaller. DONE
    5. Process list of images for Duplicates. 
    6. Process list of images for Faces. DONE
    7. Process list of images for Blurs. DONE
    8. Process list of images for Blinks. DONE
    9. Process list of images for Distortions (later feature).
    10. Convert list to CSV for interpretation by other programs. DONE
    
      Typical usage example:

      Python3 app.py $path_to_smart_preview_directory 
      python3 app.py /Applications/XAMPP/xamppfiles/htdocs/AI-Cull/images/dngs-structured-small
    ********************************
    """