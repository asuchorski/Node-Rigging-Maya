import os
import json
import maya.cmds as cmds  # type: ignore

PERSISTENT_FILE_PATH = os.path.abspath("C:\\Users\\Asuch\\Desktop\\RiggingTool\\generatedObjects.json")

def loadGeneratedObjects():
    """Loads the generated objects from the JSON file."""
    if os.path.exists(PERSISTENT_FILE_PATH):
        try:
            with open(PERSISTENT_FILE_PATH, 'r') as file:
                content = file.read().strip()
                if not content:
                    return {}  # Return empty dictionary if file is empty
                return json.loads(content)
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON. Resetting file.")
            return {}  # Return empty dictionary if JSON is invalid
    else:
        return {}

def saveGeneratedObjects(objects):
    """Saves the updated dictionary of objects to the JSON file."""
    with open(PERSISTENT_FILE_PATH, 'w') as file:
        json.dump(objects, file, indent=4)

def cleanSpecificList(key):
    """Deletes objects in a specified list and removes them from JSON."""
    generated_objects = loadGeneratedObjects()

    if key in generated_objects:
        objects_to_delete = generated_objects[key]

        # Delete objects if they exist in the scene
        existing_objects = [obj for obj in objects_to_delete if cmds.objExists(obj)]
        if existing_objects:
            cmds.delete(existing_objects)
            print(f"Deleted objects: {existing_objects}")

        # Reset the list instead of deleting the key
        generated_objects[key] = []  # Reset the list to be empty

        saveGeneratedObjects(generated_objects)  # Save changes
    else:
        print(f"No objects found for key: {key}")

def addObjectToList(key, new_object):
    """Adds a new object to a specific list inside the JSON file, after cleaning old objects."""
    generated_objects = loadGeneratedObjects()  # Load current data

    # If the key does not exist, create an empty list for it
    if key not in generated_objects:
        generated_objects[key] = []

    # Ensure no duplicates before adding
    if new_object not in generated_objects[key]:
        generated_objects[key].append(new_object)
        saveGeneratedObjects(generated_objects)  # Save changes