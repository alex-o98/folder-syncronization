from hashlib import md5
import os
import shutil

import time
from datetime import datetime

# File name definition (path is relative)
SOURCE_NAME = "source"
COPY_NAME = "replica"
LOG_NAME = "log.txt"

last_modified = None

def log(file_name,msg):
    date_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    message = msg+" "+file_name+" at "+date_time
    print(message)
    with open(LOG_NAME, 'a') as f:
        f.write(message+'\n')

def run_sync():
    """
    We walk through the source directory.
    If the files/folders do not exist in the replica folder, we create them.
    If the files exist but the MD5 are not the same, we copy the file
    If the files in the replica do not match the ones in source, we delete the ones
    who do not match (We delete them from the replica folder)

    This cycle runs once every 3 seconds and everything is logged in console
    and in a file called log.txt

    The names of the folders and the log file can be changed at the top of the file

    No external libraries have been used, so there is no need to pip install anything :)
    """
    while(True):
        time.sleep(3)
        for root, _, files in os.walk(SOURCE_NAME, topdown=False):
            # We go through each file. Each file has a root directory.
            # For example "source/one/..." from which we need only the name
            
            true_root = root

            root = root.replace("source\\","")
            root = root.replace("source","")
                
            for file_name in files:
                # Replacing the source folder name from root
                source_file = os.path.join(true_root,file_name)


                dest_dir = os.path.join(COPY_NAME,root)
                dest_file = os.path.join(dest_dir,file_name)

                # Create the files and dirs if they do not exists
                if not os.path.exists(dest_file):
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    shutil.copy(source_file,dest_file)
                    log(dest_file,"CREATED")

                # If the file already exists:    
                # Check if the files are edited with MD5 signature
                else:
                    source_contents = open(source_file,'rb')
                    dest_contents = open(dest_file,'rb')

                    # We hash the contents of the files in md5 and check them together
                    # if they are not the same we copy the source into the destination
                    if md5(source_contents.read()).hexdigest() != md5(dest_contents.read()).hexdigest():
                        shutil.copy(source_file,dest_file)
                        log(dest_file, "EDITED")

                    source_contents.close()
                    dest_contents.close()                

        # Check for file deletion
        # for this I thought about checking the files in replica to see if they still
        # exist in source. If they do not, we delete them.

        for root, _, files in os.walk(COPY_NAME, topdown=False):

            # We go through each file. Each file has a root directory.
            # For example "replica/one/..." from which we need only the name

            # Replacing the replica folder name from root

            true_root = root
            root = root.replace("replica\\","")
            root = root.replace("replica","")

            for file_name in files:
                replica_file = os.path.join(true_root,file_name)

                source_dir = os.path.join(SOURCE_NAME,root)
                source_file = os.path.join(source_dir,file_name)

                if not os.path.exists(source_dir):
                    shutil.rmtree(true_root)
                    log(true_root,"DELETE")
                    continue
                if not os.path.exists(source_file):
                    os.remove(replica_file)
                    log(replica_file,"DELETE")

if __name__ == '__main__':
    run_sync()