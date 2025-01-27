import shutil # shutil.move

import sqlite3
import os



def read_lightroom_ratings(catalog_path):
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
                AND Adobe_images.captureTime BETWEEN '2024-09-30' AND '2024-10-05';
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        for row in results:
            image_id, pick, filename = row
            print(f"Image ID: {image_id}, Pick: {pick}, Filename: {filename}")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()
        




if __name__ == "__main__":
    # Replace with path to your Lightroom catalog
    catalog_path = "/Users/sishanlong/Pictures/Lightroom/Lightroom Catalog-v13-5.lrcat"

    if not os.path.exists(catalog_path):
        print("Catalog file not found. Please check the path.")
        exit()

    read_lightroom_ratings(catalog_path)
    