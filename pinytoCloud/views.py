# coding=utf-8
"""
This File is part of Pinyto
"""
from hashlib import sha256
from Crypto.Random import get_random_bytes
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from project_path import project_path
from service.response import json_response
from pinytoCloud.models import User, StoredPublicKey, Session, Assembly, ApiFunction, Job
from pinytoCloud.settings import PINYTO_KEY
from pinytoCloud.checktoken import check_token


def home(request):
    """
    This view serves static content. Namely index.html which may bootstrap an
    Angular application at the client.

    @param request:
    @return:
    """
    with open(project_path("webapps/pinyto/backoffice/index.html"), 'r') as index_html_file:
        return HttpResponse(index_html_file.read(), content_type='text/html')


@csrf_exempt
def authenticate_request(request):
    """
    Creates a token and registers the authentication request for the username.
    Returns an encrypted token and the matching signature.
    This function only extracts the params from the request and calls authenticate.

    @param request:
    @return: json {encrypted_token: string, signature: string}
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Your request contained no valid JSON data. " +
                                       "You have to supply a username and a key_hash to authenticate."})
    if 'username' not in request_data or 'key_hash' not in request_data:
        return json_response({'error': "You have to supply a username and a key_hash to authenticate."})
    return json_response(authenticate(request_data['username'], request_data['key_hash']))


def authenticate(username, key_hash):
    """
    Creates a token and registers the authentication request for the username.
    Returns an encrypted token and the matching signature

    @param username: string
    @param key_hash: string
    @return: json {encrypted_token: string, signature: string}
    """
    try:
        user = User.objects.filter(name=username).all()[0]
    except IndexError:
        return {'error': "User '" + username + "' is unknown. Please register first."}
    try:
        key = user.keys.filter(key_hash=key_hash).exclude(active=False).all()[0]
    except IndexError:
        return {'error': "This is not a registered and active public key of this user."}
    session = user.start_session(key)
    encrypted_token = session.get_encrypted_token()
    hasher = sha256()
    hasher.update(encrypted_token)
    signature = PINYTO_KEY.sign(hasher.hexdigest(), get_random_bytes(16))
    return {'encrypted_token': encrypted_token, 'signature': unicode(signature[0])}


@csrf_exempt
def logout(request):
    """
    Ends the session with the given token.

    @param request:
    @return: json
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Please supply the token as JSON."})
    if 'token' not in request_data:
        return json_response({'error': "Please supply JSON with a token key."})
    session = check_token(request_data['token'])
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        session.delete()
    else:
        # session is not a session so it has to be response object with an error message
        return session


@csrf_exempt
def list_keys(request):
    """
    Returns a list of keys for the active account.

    @param request:
    @return: json
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Please supply the token as JSON."})
    if 'token' not in request_data:
        return json_response({'error': "Please supply JSON with a token key."})
    session = check_token(request_data['token'])
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        key_list = []
        for key in session.user.keys.all():
            key_list.append({
                'key_hash': key.key_hash,
                'active': key.active
            })
        return json_response(key_list)
    else:
        # session is not a session so it has to be response object with an error message
        return session


@csrf_exempt
def set_key_active(request):
    """
    Sets the transferred active state for the key.

    @param request:
    @return: json
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Please supply the token as JSON."})
    if 'token' not in request_data:
        return json_response({'error': "Please supply JSON with a token key."})
    session = check_token(request_data['token'])
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        if 'key_hash' not in request_data or 'active_state' not in request_data:
            return json_response({'error': "You have to supply a key_hash and an active_state."})
        if session.user.keys.filter(active=True).exclude(key_hash=request_data['key_hash']).count() < 1:
            return json_response(
                {'error': "You are deactivating your last active key. " +
                          "That is in all possible scenarios a bad idea so it will not be done."}
            )
        key = session.user.keys.get(key_hash=request_data['key_hash'])
        if request_data['active_state']:
            key.active = True
        else:
            key.active = False
        key.save()
        return json_response({'success': True})
    else:
        # session is not a session so it has to be response object with an error message
        return session


@csrf_exempt
def delete_key(request):
    """
    Deletes the specified key. This will raise an error if you try to delete your last key.

    @param request: Django request
    @return: json
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Please supply the token as JSON."})
    if 'token' not in request_data:
        return json_response({'error': "Please supply JSON with a token key."})
    session = check_token(request_data['token'])
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        if 'key_hash' not in request_data:
            return json_response({'error': "You have to supply a key_hash."})
        if session.user.keys.filter(active=True).exclude(key_hash=request_data['key_hash']).count() < 1:
            return json_response(
                {'error': "You are deleting your last active key. " +
                          "That is in all possible scenarios a bad idea so it will not be done."}
            )
        key = session.user.keys.get(key_hash=request_data['key_hash'])
        key.delete()
        return json_response({'success': True})
    else:
        # session is not a session so it has to be response object with an error message
        return session


@csrf_exempt
def register_request(request):
    """
    Creates an account if possible and saves the public key.
    This function only extracts the params from the request and calls register.

    @param request:
    @return: json
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Please supply the username and public_key as JSON."})
    if 'username' not in request_data or 'public_key' not in request_data:
        return json_response({'error': "Please supply JSON with username and public_key."})
    return json_response(register(request_data['username'], request_data['public_key']))


def register(username, key_data):
    """
    Creates an account if possible and saves the public key.

    @param username: string
    @param key_data: string
    @return: json
    """
    if User.objects.filter(name=username).count() > 0:
        return {'error': "Username " + username + " is already taken. Try another username."}
    if 'N' not in key_data or 'e' not in key_data:
        return {'error': "The public_key is in the wrong format. The key data must consist of an N and an e."}
    try:
        n = long(key_data['N'])
        if n < pow(2, 3071):
            return {'error': "Factor N in the public key is too small. Please use at least 3072 bit."}
    except ValueError:
        return {'error': "Factor N in the public key is not a number. It has to be a long integer."}
    try:
        e = long(key_data['e'])
    except ValueError:
        return {'error': "Factor e in the public key is not a number. It has to be a long integer."}
    new_user = User(name=username)
    new_user.save()
    StoredPublicKey.create(new_user, unicode(key_data['N']), e)
    return {'success': True}


@csrf_exempt
def list_own_assemblies(request):
    """
    Returns a list of the assemblies of the user specified through the token.

    @param request: Django request
    @return: json
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Please supply the token as JSON."})
    if 'token' not in request_data:
        return json_response({'error': "Please supply JSON with a token key."})
    session = check_token(request_data['token'])
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        own_assemblies = []
        for assembly in session.user.assemblies.all():
            own_assemblies.append({
                'name': assembly.name,
                'description': assembly.description,
                'api_functions': [{
                    'name': api_function.name,
                    'code': api_function.code
                } for api_function in assembly.api_functions.all()],
                'jobs': [{
                    'name': job.name,
                    'code': job.code,
                    'schedule': job.schedule
                } for job in assembly.jobs.all()]
            })
        return json_response(own_assemblies)
    else:
        # session is not a session so it has to be response object with an error message
        return session


@csrf_exempt
def save_assembly(request):
    """
    Saves the assembly specified by its original name. This can be used to rename an assembly because the
    original name and the one specified in the data could be different.

    @param request: Django request
    @return: json
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Please supply the data as JSON."})
    if 'token' not in request_data:
        return json_response({'error': "Please supply JSON with a token key."})
    session = check_token(request_data['token'])
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        if 'original_name' in request_data and 'data' in request_data:
            assembly_data = request_data['data']
            assembly_is_new = False
            try:
                assembly = session.user.assemblies.filter(name=request_data['original_name']).all()[0]
            except IndexError:
                assembly_is_new = True
                assembly = Assembly(author=session.user)
            if 'name' not in assembly_data or 'description' not in assembly_data:
                return json_response(
                    {'error': "The assembly data lacks a name or description. Both attributes must be present."}
                )
            assembly.name = assembly_data['name']
            assembly.description = assembly_data['description']
            assembly.save()
            if 'api_functions' not in assembly_data:
                assembly_data['api_functions'] = []
            if 'jobs' not in assembly_data:
                assembly_data['jobs'] = []
            for api_function in assembly.api_functions.all():
                found = False
                for loaded_function in assembly_data['api_functions']:
                    if 'name' not in loaded_function or 'code' not in loaded_function:
                        if assembly_is_new:
                            assembly.delete()
                        return json_response(
                            {'error': "The assembly data for changing an existing function " +
                                      "lacks a name or code attribute."}
                        )
                    if api_function.name == loaded_function['name']:
                        api_function.code = loaded_function['code']
                        api_function.save()
                        found = True
                if not found:
                    api_function.delete()
            for loaded_function in assembly_data['api_functions']:
                if 'name' in loaded_function and 'code' in loaded_function:
                    if not loaded_function['name'] in [x.name for x in assembly.api_functions.all()]:
                        new_function = ApiFunction(
                            assembly=assembly,
                            name=loaded_function['name'],
                            code=loaded_function['code']
                        )
                        new_function.save()
                else:
                    if assembly_is_new:
                        assembly.delete()
                    return json_response(
                        {'error': "The assembly data lacks a name or code attribute in a api function."}
                    )
            for job in assembly.jobs.all():
                found = False
                for loaded_job in assembly_data['jobs']:
                    if 'name' not in loaded_job or 'code' not in loaded_job:
                        if assembly_is_new:
                            assembly.delete()
                        return json_response(
                            {'error': "The assembly data for changing an existing job lacks a name or code attribute."}
                        )
                    if 'schedule' in loaded_job:
                        schedule = loaded_job['schedule']
                    else:
                        schedule = 0
                    if job.name == loaded_job['name']:
                        job.code = loaded_job['code']
                        job.schedule = schedule
                        job.save()
                        found = True
                if not found:
                    job.delete()
            for loaded_job in assembly_data['jobs']:
                if 'name' in loaded_job and 'code' in loaded_job:
                    if not loaded_job['name'] in [x.name for x in assembly.jobs.all()]:
                        if 'schedule' in loaded_job:
                            schedule = loaded_job['schedule']
                        else:
                            schedule = 0
                        new_job = Job(
                            assembly=assembly,
                            name=loaded_job['name'],
                            code=loaded_job['code'],
                            schedule=schedule
                        )
                        new_job.save()
                else:
                    if assembly_is_new:
                        assembly.delete()
                    return json_response(
                        {'error': "The assembly data lacks a name or code attribute in a job."}
                    )
            assembly.save()
            return json_response({'success': True})
        else:
            return json_response(
                {'error': "You have to supply an original_name and the data of the new or changed assembly."}
            )
    else:
        # session is not a session so it has to be response object with an error message
        return session


@csrf_exempt
def delete_assembly(request):
    """
    Deletes the assembly specified by its name.

    @param request: Django request
    @return: json
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Please supply the data as JSON."})
    if 'token' not in request_data:
        return json_response({'error': "Please supply JSON with a token key."})
    session = check_token(request_data['token'])
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        if 'name' not in request_data:
            return json_response(
                {'error': "You have to supply the name of the assembly you want to delete."}
            )
        try:
            assembly = session.user.assemblies.filter(name=request_data['name']).all()[0]
        except IndexError:
            return json_response(
                {'error': "There was no assembly found with the name " + request_data['name'] + "."}
            )
        assembly.delete()
        return json_response({'success': True})
    else:
        # session is not a session so it has to be response object with an error message
        return session


@csrf_exempt
def list_installed_assemblies(request):
    """
    Returns a list of the assemblies the user marked as installed.

    @param request: Django request
    @return: json
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Please supply the data as JSON."})
    if 'token' not in request_data:
        return json_response({'error': "Please supply JSON with a token key."})
    session = check_token(request_data['token'])
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        installed_assemblies = []
        for assembly in session.user.installed_assemblies.all():
            installed_assemblies.append({
                'name': assembly.name,
                'author': assembly.author.name,
                'description': assembly.description
            })
        return json_response(installed_assemblies)
    else:
        # session is not a session so it has to be response object with an error message
        return session


@csrf_exempt
def list_all_assemblies(request):
    """
    Returns a list of all assemblies.

    @param request: Django request
    @return: json
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Please supply the data as JSON."})
    if 'token' not in request_data:
        return json_response({'error': "Please supply JSON with a token key."})
    session = check_token(request_data['token'])
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        all_assemblies = []
        for assembly in Assembly.objects.all():
            all_assemblies.append({
                'name': assembly.name,
                'author': assembly.author.name,
                'description': assembly.description
            })
        return json_response(all_assemblies)
    else:
        # session is not a session so it has to be response object with an error message
        return session


@csrf_exempt
def install_assembly(request):
    """
    Adds the assembly specified by author and name to the installed assemblies of the user.

    @param request: Django request
    @return: json
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Please supply the data as JSON."})
    if 'token' not in request_data:
        return json_response({'error': "Please supply JSON with a token key."})
    session = check_token(request_data['token'])
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        if 'author' in request_data:
            try:
                author = User.objects.filter(name=request_data['author']).all()[0]
            except IndexError:
                return json_response(
                    {'error': "There was no user found with the name " + request_data['author'] + "."}
                )
        else:
            return json_response(
                {'error': "You have to supply an author to install an assembly."}
            )
        if 'name' in request_data:
            try:
                assembly = author.assemblies.filter(name=request_data['name']).all()[0]
            except IndexError:
                return json_response(
                    {'error': "There was no assembly found with the name " + request_data['author'] + "/" +
                              request_data['name'] + "."}
                )
        else:
            return json_response(
                {'error': "You have to supply the name of the assembly you want to install."}
            )
        session.user.installed_assemblies.add(assembly)
        return json_response({'success': True})
    else:
        # session is not a session so it has to be response object with an error message
        return session


@csrf_exempt
def uninstall_assembly(request):
    """
    Removes the assembly specified by author and name from the installed assemblies of the user.

    @param request: Django request
    @return: json
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Please supply the data as JSON."})
    if 'token' not in request_data:
        return json_response({'error': "Please supply JSON with a token key."})
    session = check_token(request_data['token'])
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        if 'author' in request_data and 'name' in request_data:
            try:
                assembly = session.user.installed_assemblies.filter(
                    author__name=request_data['author']
                ).filter(
                    name=request_data['name']
                ).all()[0]
            except IndexError:
                return json_response(
                    {'error': "There was no installed assembly found with the name " + request_data['author'] +
                              "/" + request_data['name'] + "."}
                )
        else:
            return json_response(
                {'error': "You have to supply an author and a name to uninstall an assembly."}
            )
        session.user.installed_assemblies.remove(assembly)
        return json_response({'success': True})
    else:
        # session is not a session so it has to be response object with an error message
        return session


@csrf_exempt
def get_assembly_source(request):
    """
    Fetches the sourcecode of the assebly specified by author and name.

    @param request: Django request
    @return: json
    """
    try:
        request_data = json.loads(request.body)
    except ValueError:
        return json_response({'error': "Please supply the data as JSON."})
    if 'token' not in request_data:
        return json_response({'error': "Please supply JSON with a token key."})
    session = check_token(request_data['token'])
    # check_token will return an error response if the token is not found or can not be verified.
    if isinstance(session, Session):
        if 'author' in request_data:
            try:
                author = User.objects.filter(name=request_data['author']).all()[0]
            except IndexError:
                return json_response(
                    {'error': "There was no user found with the name " + request_data['author'] + "."}
                )
        else:
            return json_response(
                {'error': "You have to supply an author to identify the assembly."}
            )
        if 'name' in request_data:
            try:
                assembly = author.assemblies.filter(name=request_data['name']).all()[0]
            except IndexError:
                return json_response(
                    {'error': "There was no assembly found with the name " + request_data['author'] + "/" +
                              request_data['name'] + "."}
                )
        else:
            return json_response(
                {'error': "You have to supply the name of the assembly."}
            )
        return json_response({
            'api_functions': [{
                'name': f.name,
                'code': f.code
            } for f in assembly.api_functions.all()],
            'jobs': [{
                'name': f.name,
                'code': f.code,
                'schedule': f.schedule
            } for f in assembly.jobs.all()]
        })
    else:
        # session is not a session so it has to be response object with an error message
        return session