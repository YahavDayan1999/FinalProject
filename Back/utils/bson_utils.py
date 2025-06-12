from bson import ObjectId

def convert_objectid(doc):
    if isinstance(doc, list):
        return [convert_objectid(d) for d in doc]
    elif isinstance(doc, dict):
        return {
            k: convert_objectid(v)
            for k, v in doc.items()
        }
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc