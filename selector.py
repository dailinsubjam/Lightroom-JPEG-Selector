import shutil # shutil.move
import sqlite3
import os
import argparse
from dataclasses import dataclass

@dataclass
class ProcessArgs:
    catalog_path: str
    jpg_folder_path: str
    new_folder_path: str
    start_date: str
    end_date: str

# parse the command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Process Lightroom catalog.')
    parser.add_argument('--catalog', type=str, default="/Users/sishanlong/Pictures/Lightroom/Lightroom Catalog-v13-5.lrcat", help='Path to Lightroom catalog')
    parser.add_argument('--jpg_folder_path', type=str, default="/Users/sishanlong/Pictures/2025.03@EarlySpringLathamSt", help='Path to the folder containing the .JPG files')
    parser.add_argument('--new_folder_path', type=str, default="/Users/sishanlong/Pictures/2025.03@EarlySpringLathamSt/selected_JPG", help='Path to the new folder')
    parser.add_argument('--start_date', type=str, default="2025-03-25", help='Start date')
    parser.add_argument('--end_date', type=str, default="2025-04-06", help='End date')
    return parser.parse_args()


# transfer the name from .NEF file to .JPG file
def get_jpg_name(filename):
    # If the filename contains "-", then only keep the part before "-" 
    # or else keep the part before the last "."
    # and add ".JPG" to the end
    if "-" in filename:
        return filename.split("-")[0] + ".JPG"
    else:
        return filename.split(".")[0] + ".JPG"

def read_lightroom_ratings(catalog_path, start_date, end_date):
    """
    Read image ratings directly from Lightroom catalog
    
    Args:
        catalog_path (str): Path to the .lrcat file
        
    Returns:
        list: Dictionary containing file info and ratings
    """


    # Connect to the catalog database
    conn = sqlite3.connect(catalog_path)
    cursor = conn.cursor()

    # PRAGMA command to get the table schema
    try:    
        print("Table schema for Adobe_images:")
        cursor.execute("PRAGMA table_info(Adobe_images);")
        schema = cursor.fetchall()
        for column in schema:
            print(column)

        print("Table schema for AgLibraryFile:")
        cursor.execute("PRAGMA table_info(AgLibraryFile);")
        schema = cursor.fetchall()
        for column in schema:
            print(column)

        cursor.execute("SELECT COUNT(*) FROM Adobe_images;")
        row_count = cursor.fetchone()[0]
        print(f"Total rows in Adobe_images: {row_count}")

        print("\nFirst 10 rows from AgLibraryFile:")
        cursor.execute("SELECT * FROM AgLibraryFile LIMIT 10;")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error: {e}")

    # get the list of .JPG we want
    jpg_files = []

    try:
        # Query to get file paths and their ratings
        # Adobe_images table contains the basic image info
        # AgHarvestedIptcMetadata contains metadata including ratings
        query = """
            SELECT 
                Adobe_images.id_local AS image_id,
                Adobe_images.pick,
                AgLibraryFile.originalFilename AS filename
            FROM 
                Adobe_images
            INNER JOIN 
                AgLibraryFile
            ON 
                Adobe_images.rootFile = AgLibraryFile.id_local
            WHERE 
                Adobe_images.pick = 1
                AND Adobe_images.captureTime BETWEEN ? AND ?;
        """

        
        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()

        for row in results:
            image_id, pick, filename = row
             # get the name of the .JPG file
            jpg_name = get_jpg_name(filename)
            print(f"Image ID: {image_id}, Pick: {pick}, Filename: {filename}, JPG Name: {jpg_name}")
            jpg_files.append(jpg_name)
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

    return jpg_files

def move_jpg_files(jpg_folder_path, new_folder_path, jpg_files):
    # create the new folder if it doesn't exist
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)

    # copy the .JPG files to the new folder
    for jpg_file in jpg_files:
        shutil.copy(jpg_folder_path + "/" + jpg_file, new_folder_path + "/" + jpg_file)

if __name__ == "__main__":
    args = parse_args()
    catalog_path = args.catalog

    if not os.path.exists(catalog_path):
        print("Catalog file not found. Please check the path.")
        exit()

    jpg_files = read_lightroom_ratings(catalog_path, args.start_date, args.end_date)
    print(f"Total .JPG files: {len(jpg_files)}")

    # find the .JPG files in the given folder and copy them to the new folder
    move_jpg_files(args.jpg_folder_path, args.new_folder_path, jpg_files)
    