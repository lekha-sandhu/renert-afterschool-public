from root import app, db

# Add helper objects to the shell context of "flask shell"
@app.shell_context_processor
def make_shell_context():
    terms = { 'db' :  db,
              'app' : app }

    # Get list of all registered db.Model classes
    # see: https://stackoverflow.com/a/44651441
    db_classes = [cls for cls in db.Model.registry._class_registry.values()
                  if isinstance(cls, type) and issubclass(cls, db.Model)]
    for x in db_classes:
        terms[x.__name__] = x
    return terms
