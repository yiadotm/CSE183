from py4web import action, request, abort, redirect, URL
from py4web.utils.form import Form
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash

@action("index")
def index():
    redirect(URL('static', 'index.html')) 
    


    
@action('/bird_spotter/api/birds', method='POST')
@action.uses(db)
def api_birds_post():
    # bird_info = request.json
    # print('Received bird info:', bird_info)  # Log the received bird info

    result = db.bird.validate_and_insert(**request.json)

    bird_id = result['id'] if result['id'] else None
    print('Database insertion result:', result)  # Log the database insertion result

    print('New bird ID:', bird_id)

    return dict(id=bird_id, errors=result['errors'])


@action('/bird_spotter/api/birds', method='GET')
@action.uses(db)
def api_birds_get():
    birds = db(db.bird).select().as_list()
    for bird in birds:
        bird['habitat'] = bird.get('habitat', '')
        bird['weight'] = bird.get('weight', 0)
        bird['sightings'] = bird.get('sightings', 0)
    return dict(birds=birds)


@action("/bird_spotter/api/birds/<id>/increase_sightings", method="POST")
@action.uses(db)
def increase_sightings(id):
    bird = db(db.bird.id == id).select().first()
    if bird is None:
        return dict(success=False, errors="Bird not found")
    db(db.bird.id == id).update(sightings=bird.sightings + 1)
    db.commit()  # Add this line to commit the changes
    return dict(success=True, updated=True, errors={})


@action("/bird_spotter/api/birds/<id>", method="PUT")
@action.uses(db)
def update_bird(id=None):
    try:
        # bird_info = request.json
        if id is not None:
            data = request.json
            data.pop('id', None)  
            data.pop('name', None)  
            result = db(db.bird.id == id).validate_and_update(**request.json)
            print('Update result:', result['updated'])
            if 'updated' in result and result['updated'] > 0:
                db.commit()
                return dict(success=True, updated=result['updated'], errors={})
            else:
                print( "Response: " ,dict(success=False, errors=result['errors']))
                return dict(success=False, errors=result['errors'])
    except Exception as e:
        print('Exception:', e) 
        return dict(error=str(e))
    return dict(error='Bird not found')

@action("/bird_spotter/api/birds/<id>", method="DELETE")
@action.uses(db)
def _(id=None):
    if id is not None:
        db(db.bird.id == id).delete()
        return dict(success=True)
    return dict(error='Bird not found')


# @action("api/entries", method="GET")
# @action.uses(db)
# def _():
#     rows = db(db.entry).select(orderby=~db.entry.post_date, limitby=(0,100))
#     return {"entries": rows.as_list()}

# @action("api/entries", method="POST")
# @action.uses(db, auth.user)
# def _():
#     data = request.json    
#     return db.entry.validate_and_insert(**data)

# @action("api/entries/<entry_id>", method="GET")
# @action.uses(db)
# def _(entry_id):
#     rows = db(db.entry.id==entry_id).select()
#     return {"entries": rows.as_list()}

# @action("api/entries/<entry_id>", method="DELETE")
# @action.uses(db, auth.user)
# def _():
#     db(db.entry.id==entry_id).delete()
#     return {}

# @action("api/entries/<entry_id>", method="PUT")
# @action.uses(db, auth.user)
# def _(entry_id):
#     data = request.json
#     return db.entry.validate_and_update(entry_id, **data)    

# @action("api/entries/<entry_id>/comments", method="GET")
# @action.uses(db)
# def _(entry_id):
#     rows = db(db.comment.entry_id==entry_id).select(orderby=db.comment.post_date)
#     return {"comments": rows.as_list()}

# @action("api/entries/<entry_id>/comments", method="POST")
# @action.uses(db,auth.user)
# def _(entry_id):
#     db.comment.entry_id.default = entry_id
#     return db.comment.validate_and_insert(**request.json)



