"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""
#url_signer = URLSigner(session)

import uuid

from py4web import action, request, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner

from yatl.helpers import A
from . common import db, session, T, cache, auth, signed_url

from . models import get_user_email

url_signer = URLSigner(session)


@action('index', method='GET')
@action.uses('index.html', db)
def view_products():
    # We get all the table rows, via a query.
    sort = request.params.get('sort')
    if sort == 'asc1':
        rows = db().select(db.product.ALL, orderby=db.product.product_name)
    elif sort == 'desc1':
        rows = db().select(db.product.ALL, orderby=~db.product.product_name)
    elif sort == 'asc2':
        rows = db().select(db.product.ALL, orderby=db.product.vocabulary)
    elif sort == 'desc2':
        rows = db().select(db.product.ALL, orderby=~db.product.vocabulary)
    elif sort == 'asc3':
        rows = db().select(db.product.ALL, orderby=db.product.active)
    elif sort == 'desc3':
        rows = db().select(db.product.ALL, orderby=~db.product.active)
    elif sort == 'asc4':
        rows = db().select(db.product.ALL, orderby=db.product.creation_date)
    elif sort == 'desc4':
        rows = db().select(db.product.ALL, orderby=~db.product.creation_date)
    else:
        rows = db(db.product).select()
    return dict(rows=rows, signed_url = signed_url, sort = sort)

@action('add_product', method=['GET', 'POST'])
@action.uses('product_form.html', session, db)
def add_product():
    form = Form(db.product, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form)

@action('edit_product/<product_id>', method=['GET', 'POST'])
@action.uses('product_form.html', session, db)
def edit_product(product_id=None):
    """Note that in the above declaration, the product_id argument must match
    the <product_id> argument of the @action."""
    # We read the product.
    p = db.product[product_id]
    if p is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    form = Form(db.product, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form)
#@action('delete/<id>', method=['GET', 'POST'])
#@action.uses(session)
#def (id=None):
    # Note that id is an int, due to the type declaration.
#    if id is not None:
        # In a session, all keys need to be strings.
#        db(db.product.product_id == id).delete()
#    redirect(URL('index'))

@action('delete_product/<product_id>', method=['GET', 'POST'])
@action.uses('product_form.html', session, db, signed_url.verify())
def delete_product(product_id=None):
    if product_id is None:
        redirect(URL('index'))
    else:
        db(db.product.id == product_id).delete()
        redirect(URL('index'))
#inser

# @action('edit_phone/<product_id>', method=['GET', 'POST'])
# @action.uses('flow.html', session, db)
# def edit_phone(product_id=None):
#     #contacts = db(db.contacts.id == contactID).select()
    
#     products = db(db.product.id == product_id).select()
#     product = products[0]
    
#     return dict(add_post_url = URL('add_post', signer=url_signer),
#     flow=product.flow
#     )

# @action('add_post/<product_id>', method="POST")
# @action.uses(url_signer.verify(), db, auth.user)
# def add_post(productID=None):
#     p = request.json.get('post_text')
#     product = db(db.product.id == productID).select()
#     product = products[0]
#     product.flow=p
#     return dict(flow=product.flow)
#proj5 solution
def get_name(email):
    r = db(db.auth_user.email == email).select().first()
    return r.first_name + " " + r.last_name if r is not None else "Unknown"

def get_rating(post):
    r = db((db.thumb.post_id == post.id)
           & (db.thumb.user_email == get_user_email())).select()
    rr = r.first()
    if rr is None:
        return 0
    else:
        return rr.get('rating')

def get_all_posts(product_id):
    all_posts = db(db.post.user_email==product_id).select(
                            orderby=db.post.ts)#~
    formatted = []
    index=0
    for j in all_posts:
        index+=1
        #name = get_name(j.user_email) db.post.ALL,
        name = j.id
        is_owner = j.user_email
        is_thumbs_up = get_rating(j) or 0
        formatted_entry = {'post_id': j.id,
                           'text': j.post_text,
                           'author': index,
                           'thumbs': is_thumbs_up,
                           'is_owner': is_owner,
                           'value': resolve_values(j.post_text, formatted, is_owner)}
        formatted.append(formatted_entry)
    return formatted

def run_flow(product_id, input):
    all_posts = db(db.post.user_email==product_id).select(
                            orderby=db.post.ts)#~
    formatted = []
    index=0
    print(input)
    for j in all_posts:
        index+=1
        #name = get_name(j.user_email) db.post.ALL,
        if index>len(input):
            name = j.id
            is_owner = j.user_email
            is_thumbs_up = get_rating(j) or 0
            formatted_entry = {'post_id': j.id,
                            'text': j.post_text,
                            'author': index,
                            'thumbs': is_thumbs_up,
                            'is_owner': is_owner,
                            'value': resolve_values(j.post_text, formatted, is_owner)}
            formatted.append(formatted_entry)
        else:
            name = j.id
            is_owner = j.user_email
            is_thumbs_up = get_rating(j) or 0
            formatted_entry = {'post_id': j.id,
                            'text': j.post_text,
                            'author': index,
                            'thumbs': is_thumbs_up,
                            'is_owner': is_owner,
                            'value': input[index-1]}
            formatted.append(formatted_entry)
    if formatted[index-1]["value"]==False:
        return formatted[index-2]["value"]
    if formatted[index-1]["value"]==True:
        newinput=[]
        print("new", len(input))
        for k in range(index-len(input)-1, index-1):
            newinput.append(formatted[k]["value"])
            
        return run_flow(product_id, newinput)
    

@action('edit_phone/<product_id>')
@action.uses('flow.html', url_signer, auth.user, db)
def edit_phone(product_id=None):
    print(product_id)
    return dict(
        product_id=product_id,
        insert_post_url = URL('insert_post', product_id, signer=url_signer),
        get_posts_url = URL('get_posts', product_id, signer=url_signer),
        add_post_url = URL('add_post',product_id, signer=url_signer),
        get_likers_url = URL('get_likers', signer=url_signer),
        get_haters_url = URL('get_haters', signer=url_signer),
        thumb_url = URL('thumb', signer=url_signer),
        delete_post_url = URL('delete_post', product_id, signer=url_signer),
        edit_post_url = URL('edit_post', product_id, signer=url_signer),
        send_text_url = URL('send_text', signer=url_signer),
        copy_posts_url = URL('copy_posts', product_id, signer=url_signer),
        user_email = get_user_email(),
        username = auth.current_user.get('first_name') + " " + auth.current_user.get("last_name")
    )

@action('get_posts/<product_id>')
@action.uses(url_signer.verify(), db, auth.user)
def get_posts(product_id):
    posts = get_all_posts(product_id)
    print("posts")
    return dict(posts=posts)

@action('add_post/<product_id>', method="POST")
@action.uses(url_signer.verify(), db, auth.user)
def add_post(product_id):
    p = request.json.get('post_text')
    db.post.insert(user_email=product_id, post_text=p)
    posts = get_all_posts(product_id)
    return dict(posts=posts)

@action('copy_posts/<product_id>', method="POST")
@action.uses(url_signer.verify(), db, auth.user)
def copy_posts(product_id):
    print("started")
    p = request.json.get('post_text')
    copy_posts = db(db.post.user_email==int(p)).select(orderby=db.post.ts)
    for pos in copy_posts:
    #db.post.insert(user_email=product_id, post_text=p)
    #posts = get_all_posts(product_id)
        db.post.insert(user_email=product_id, post_text=pos.post_text)
    posts = get_all_posts(product_id)
    return dict(posts=posts)


@action('insert_post/<product_id>', method="POST")
@action.uses(url_signer.verify(), db, auth.user)
def insert_post(product_id):
    print(product_id)
    p = request.json.get('post_id')
    db.post.insert(user_email=product_id, post_text="")
    all_posts = db(db.post.user_email==product_id).select(
                            orderby=db.post.ts)
    i=len(db(db.post.user_email == product_id).select())
    print("eye",i)
    print("ekans", p)
    posts = get_all_posts(product_id)
    cat=False
    j=0
    for j in posts[::-1]:
        print("arbok",j["post_id"])
        if cat:
            print("debug", klop["post_id"])
            print(db(db.post.id == j["post_id"]).select()[0].post_text)
            db(db.post.id == klop["post_id"]).select()[0].update_record(post_text=db(db.post.id == j["post_id"]).select()[0].post_text)
            if klop['post_id']==p:
                print("ook")
                db(db.post.id == klop["post_id"]).select()[0].update_record(post_text="")
                cat=False
                break
        else:
            cat=True
        klop=j
    if cat:
        print("abrac")
        db(db.post.id == posts[0]["post_id"]).select()[0].update_record(post_text="")
    posts = get_all_posts(product_id)

    return dict(posts=posts)

@action('edit_post/<product_id>', method="POST")
@action.uses(url_signer.verify(), db, auth.user)
def edit_post(product_id):
    print("ekans")
    p = request.json.get('post_id')
    print(p)
    post = request.json.get('post_text')
    db(db.post.id == p).select()[0].update_record(post_text=post)
    print("changing," + db(db.post.id == p).select()[0].post_text)
    posts = get_all_posts(product_id)
    return dict(posts=posts)

@action('thumb', method="POST")
@action.uses(url_signer.verify(), db, auth.user)
def thumb():
    p = request.json.get('post_id')
    r = request.json.get('rating')
    t = db((db.thumb.post_id == p) & (db.thumb.user_email == get_user_email())).select()
    if len(t) == 0:
        db.thumb.insert(post_id=p,
                        user_email=get_user_email(),
                        rating=r)
    else:
        db((db.thumb.post_id == p) & (db.thumb.user_email == get_user_email())).update(rating=r)
    return "ok"

@action('get_likers')
@action.uses(url_signer.verify(), db, auth.user)
def get_likers():
    p = request.params.get('post_id')
    l = db((db.thumb.post_id == p) & (db.thumb.rating == 1)).select()
    j = 0
    ret_str = ""
    for i in l:
        if j == 0:
            ret_str = "Liked by " + get_name(i.user_email)
        elif j == 1 and len(l) == 2:
            ret_str += ' and ' + get_name(i.user_email)
        elif j == len(l) - 1:
            ret_str += ', and ' + get_name(i.user_email)
        else:
            ret_str += ', ' + get_name(i.user_email)
        j += 1
    ret_str = ret_str + '.' if len(ret_str) > 0 else ""
    return ret_str

@action('get_haters')
@action.uses(url_signer.verify(), db, auth.user)
def get_likers():
    p = request.params.get('post_id')
    h = db((db.thumb.post_id == p) & (db.thumb.rating == -1)).select()
    j = 0
    ret_str = ""
    for i in h:
        if j == 0:
            ret_str = "Disliked by " + get_name(i.user_email)
        elif j == 1 and len(h) == 2:
            ret_str += ' and ' + get_name(i.user_email)
        elif j == len(h) - 1:
            ret_str += ', and ' + get_name(i.user_email)
        else:
            ret_str += ', ' + get_name(i.user_email)
        j += 1
    ret_str = ret_str + '.' if len(ret_str) > 0 else ""
    return ret_str

@action('delete_post/<product_id>', method="POST")
@action.uses(url_signer.verify(), db, auth.user)
def delete_post(product_id):
    p = request.json.get('post_id')
    u_e = db(db.post.id == p).select().first()
    if u_e.get('user_email') == product_id:
        db(db.post.id == p).delete()
    posts = get_all_posts(product_id)
    return dict(posts=posts)

#@action('edit_post', method="POST")
#@action.uses(url_signer.verify(), db, auth.user)
#def edit_post():
#        redirect(URL('edit_posts', post_id))
@action('send_text', method="POST")
@action.uses(url_signer.verify(), db, auth.user)
def send_text():
    print("ran")
    p = request.json.get('post_id')
    try:
        text=db(db.post.id == p).select()[0].post_text
    except:
        print(p)
        text=""
    print(text)
    return dict(text=text)


@action.uses(db, auth.user)
def resolve_value1(text, formatted):
    print(formatted)
    ekans=-1
    index=0
    while index in range(0,len(text)):
        print(text[index])
        if text[index]=='^':
            print("ekans")
            if ekans==-1:
                ekans =index

            elif ekans!=-1:
                print("c", ekans, index)
                token=text[ekans+1:index]
                print(token)
                args=token.split(';')
                cat=False
                for lopaka in args:
                    if cat:
                        print("if", prev)
                        if resolve_value1(prev, formatted)==True:
                            text=lopaka
                            
                            break
                    else:
                        cat=True
                    prev=lopaka
                if "^" in text:
                    text="invalid"
                else:
                    break
        index+=1
    ekans=-1
    index=0
    while index in range(0,len(text)):
        if text[index] == '~':
            if ekans==-1:
                ekans =index
            elif ekans!=-1:
                print("c", ekans, index)
                token=int(text[ekans+1:index])
                print(token)
                #print(formatted)
                try:
                    resolve=formatted[token-1]["value"]
                except:
                    return "bad tile resolution"
                newtext=text[:ekans]+str(resolve)+text[index+1:]
                text=newtext
                #print("text", text)
                index=ekans
                ekans=-1
        index+=1
    index=0
    ekans=-1
    print("d")
    print(text)
    while index in range(0,len(text)):
        print(text[index])
        if text[index]=='`':
            print("ekans")
            if ekans==-1:
                ekans =index

            elif ekans!=-1:
                print("c", ekans, index)
                token=text[ekans+1:index]
                print(token)
                args=token.split(',')
                flow=run_flow(args[0], args[1:])
                newtext=text[:ekans]+str(flow)+text[index+1:]
                text=newtext
                print("text", text)
                index=ekans
                ekans=-1
        index+=1
    try: 
        return eval(text)
    except:
        return "invalid"

@action.uses(db, auth.user)
def resolve_value2(text, formatted):
    print("oregon")
    if "+" not in text:
        if text=="1M":
            return "AM, A C# E"
        if text=="2M":
            return "BbM, Bb D F"
        if text=="3M":
            return "BM, B D# F#"
        if text=="4M":
            return "CM, C E G"
        if text=="5M":
            return "C#M, C# F G#"
        if text=="6M":
            return "DM, D F# A"
        if text=="7M":
            return "EbM, Eb G Bb"
        if text=="8M":
            return "EM, E G# B"
        if text=="9M":
            return "FM, F A C"
        if text=="10M":
            return "F#M, F# A# C#"
        if text=="11M":
            return "GM, G B D"
        if text=="12M":
            return "AbM, Ab C Eb"
        if text=="1m":
            return "Am, A C E"
        if text=="2m":
            return "Bbm, Bb Db F"
        if text=="3m":
            return "Bm, B D F#"
        if text=="4m":
            return "Cm, C Eb G"
        if text=="5m":
            return "C#m, C# E G#"
        if text=="6m":
            return "Dm, D F A"
        if text=="7m":
            return "Ebm, Eb Gb Bb"
        if text=="8m":
            return "Em, E G B"
        if text=="9m":
            return "Fm, F Ab C"
        if text=="10m":
            return "F#m, F# A C#"
        if text=="11m":
            return "Gm, G Bb D"
        if text=="12m":
            return "G#m, G# B D#"
         
        return "invalid"
    else:
        print("alpaca")
        add=0
        letter="m"
        ekans=-1
        index=0
        while index in range(0,len(text)):
            if text[index] == '~':
                if ekans==-1:
                    ekans =index
                elif ekans!=-1:
                    print("c", ekans, index)
                    token=int(text[ekans+1:index])
                    print(token)
                    #print(formatted)
                    try:
                        resolve=formatted[token-1]["text"]
                        letter=resolve[len(resolve)-1]
                    except:
                        return "bad tile resolution"
                    number=int(resolve.split(letter)[0])
                    print("klop",text[len(text)-1], number, resolve)
                    if "M" in resolve:
                        if text[len(text)-1]=="2":
                            add=2
                            letter="m"
                        elif text[len(text)-1]=="3":
                            add=4
                            letter="m"
                        elif text[len(text)-1]=="4":
                            add=5
                            letter="M"
                        elif text[len(text)-1]=="5":
                            add=7
                            letter="M"
                        elif text[len(text)-1]=="6":
                            add=9
                            letter="m"
                        elif text[len(text)-1]=="7":
                            add=11
                            letter="m"
                        elif text[len(text)-1]=="8":
                            add=12
                            letter="M"
                    if "m" in resolve:
                        print("entering", text[len(text)-1]==str(3))
                        if text[len(text)-1]=="2":
                            add=2
                            letter="m"
                        elif text[len(text)-1]=="3":
                            print("here")
                            add=3
                            letter="M"
                        elif text[len(text)-1]=="4":
                            add=5
                            letter="m"
                        elif text[len(text)-1]=="5":
                            add=7
                            letter="M"
                        elif text[len(text)-1]=="6":
                            add=8
                            letter="M"
                        elif text[len(text)-1]=="7":
                            add=10
                            letter="M"
                        elif text[len(text)-1]=="8":
                            add=12
                            letter="m"
                    carpet=(number+add)%12
                    string=str(carpet) + letter
                    print(carpet)
                    return resolve_value2(string, formatted)
                    #newtext=text[:ekans]+str(resolve)+text[index+1:]
                    #text=newtext
                    #print("text", text)
                    index=ekans
                    ekans=-1
            index+=1
        return ""
        
@action.uses(db, auth.user)
def resolve_value3(text, formatted):
    ekans=-1
    index=0
    while index in range(0,len(text)):
        if text[index] == '~':
            if ekans==-1:
                ekans =index
            elif ekans!=-1:
                print("c", ekans, index)
                token=int(text[ekans+1:index])
                print(token)
                #print(formatted)
                try:
                    resolve=formatted[token-1]["value"].split("| ")[0]
                except:
                    return "bad tile resolution"
                newtext=text[:ekans]+str(resolve)+text[index+1:]
                text=newtext
                #print("text", text)
                index=ekans
                ekans=-1
        index+=1
    ekans=-1
    index=0    
    while index in range(0,len(text)):
        if text[index] == '`':
            if ekans==-1:
                ekans =index
            elif ekans!=-1:
                print("c", ekans, index)
                token=text[ekans+1:index]
                print(token)
                return token + "| " + text.replace("`","")
                ekans=-1
        index+=1

@action.uses(db, auth.user)    
def resolve_values(text, formatted, is_owner):
    print(is_owner)
    if db(db.product.id == is_owner).select()[0].vocabulary==1:
        return resolve_value1(text, formatted)
    elif db(db.product.id == is_owner).select()[0].vocabulary==2:
        return resolve_value2(text, formatted)
    else: 
        return resolve_value3(text, formatted)