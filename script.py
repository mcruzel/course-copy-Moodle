# Maxime Cruzel
# Mass create courses on Moodle
# V 0.1, 2022, July

import json
import requests

global courses_to_create
global timestamp_end_courses
global timestamp_start_courses
global format_course
global numsections_courses

token_ws_report = ""
token_ws_coursecreation = ""
ws_report = "block_configurable_reports_get_report_data"
ws_coursecreation = "core_course_create_courses"
url_moodle = ""
reportid_categories = 0
reportid_courses = 0
courses_to_create = []
timestamp_end_courses = 0
timestamp_start_courses = 0
format_course  = "tiles"
numsections_courses = 1


# At the begin : take all courses list from custom reports plugin ws
def get_report_courses():
    global ws_courses_data
    webservice_report_response_content_courses = url_moodle+"/webservice/rest/server.php?wstoken="+token_ws_report+"&wsfunction="+ws_report+"&moodlewsrestformat=json&reportid="+str(reportid_courses)
    webservice_reponse_content_courses = requests.get(webservice_report_response_content_courses)
    webservice_reponse_content_courses_py = json.loads(webservice_reponse_content_courses.text)
    ws_courses_data = webservice_reponse_content_courses_py['data']
    ws_courses_data = json.loads(ws_courses_data)

# Use WS
def get_report_categories():
    global ws_categories_data
    webservice_report_response_content_categories = url_moodle+"/webservice/rest/server.php?wstoken="+token_ws_report+"&wsfunction="+ws_report+"&moodlewsrestformat=json&reportid="+str(reportid_categories)
    webservice_reponse_content_categories = requests.get(webservice_report_response_content_categories)
    webservice_reponse_content_categories_py = json.loads(webservice_reponse_content_categories.text)
    ws_categories_data = webservice_reponse_content_categories_py['data']
    ws_categories_data = json.loads(ws_categories_data)
    
    
# Get courses and create courses (menu only)
def get_courses_from_report(category):
    global ws_courses_data
    global response_input_menu_cours
    print("Liste des cours actuels de la catégorie "+str(category))
    print("-----------------------")
    prefix = ""
    for i_courses in ws_courses_data:
        if str(i_courses['category']) == str(category):
            print(i_courses['fullname'])
            # Prefix making
            if len(i_courses['fullname'].split(" - ")) == 2 and prefix == "":
                prefix = i_courses['fullname'].split(" - ")[0]+" - "
            elif prefix == "":
                prefix = "Don't use"
                
    response_input_menu_cours = input("Entrer le fullname d'un cours à créer. Tapez -n après (et sans espace) pour utiliser le préfixe \""+prefix+"\". Tapez -r pour retourner aux catégories. Taper -c pour lancer la création des cours. > ")
    if len(response_input_menu_cours.split("-n")) == 2:
        response_input_menu_cours = prefix+response_input_menu_cours.split("-n")[0] # add the prefix and delete "-n"
        create_courses_queue(category) # go to course array append
    elif response_input_menu_cours == "-r": # if we want to return at category selection
        balayage_categories(category)
    elif response_input_menu_cours == "-c": # if we want to create courses
        create_courses(courses_to_create)
    else: # if we create a course... without parameters
        create_courses_queue(category)
        
# courses to create array append
def create_courses_queue(category):
    courses_to_create.append([response_input_menu_cours, category])
    print("*********** Queue... > "+str(courses_to_create))
    get_courses_from_report(category)
            

# data origin : ws
def balayage_categories(origin):
    global response_input_category
    global response_input_categoryid
    # select categories in which duplicate courses
    #f = open("fichierjson.json", "r")
    #json_content_from_file = json.load(f)
    count = 1
    menu_choices = [] # the array with data behing every menu choice
    response_input = ""
    
    # Indicates where we are (category)
    print("--------------")
    if origin == 0:
        print("Balayage de la catégorie [Root]")
    else:
        for i_s_cat_array_info in ws_categories_data:
            if i_s_cat_array_info['id'] == str(origin):
                print("Balayage de la catégorie ["+i_s_cat_array_info['name']+"]")
     
    # choices array building
    for i_s_cat_array in ws_categories_data:
        if i_s_cat_array['parent'] == str(origin):
            print(str(count)+" -> "+i_s_cat_array['name'])
            menu_choices.append([count,i_s_cat_array['name'], i_s_cat_array['id'], i_s_cat_array['parent']])
            count += 1
    print("(s - STOP / y - OUI / c - OUVRIR FILS (-fils) / p - RETOUR PARENT") # c-menuid (example : c-3) 
    print("--------------")
    response_input = input("Faut-il créer les cours dans cette catégorie ?")
    
    if len(response_input.split("-")) > 1 and len(menu_choices) > 0: # if there is an argumment on menu choice (-fils, -parent)
        response_input_choice = response_input.split("-")[0]
        response_input_category = response_input.split("-")[1]
    elif len(menu_choices) == 0: # if menu choices empty (because no categories on aimed category)
        response_input_choice = response_input # we have to attribute it. Remember, menu_choices is the array with data behing every menu choice
        for i_s_cat_array in ws_categories_data: # we have to attribute it
            if str(i_s_cat_array['id']) == str(origin):
                menu_choices = [[count, i_s_cat_array['name'], i_s_cat_array['id'], i_s_cat_array['parent']]] # normal structure [[ ]] because we have two indexes menu_choices
                response_input_category = i_s_cat_array['id']
        response_input_parentid = menu_choices[0][3] 
    else:
        response_input_choice = response_input
        response_input_parentid = menu_choices[0][3]
        # ne rien ajouter d'autre (erreur en cas de retour parent)

    # check the value of the menu choice
    for menu in menu_choices:
        if str(menu[0]) == response_input_category:
            response_input_category = menu[1]
            response_input_categoryid = menu[2]
            response_input_parentid = menu[3]
    
    #check the menu choices
    if response_input_choice == "c":
        balayage_categories(response_input_categoryid)
        
    elif response_input_choice == "p":
        for i_s_cat_array_prime in ws_categories_data:
            # go to category = parentid
            if str(i_s_cat_array_prime["id"]) == str(response_input_parentid):
                response_input_parentid = i_s_cat_array_prime["parent"]
                
        balayage_categories(response_input_parentid)
        
    elif response_input_choice == "y":
        get_courses_from_report(response_input_categoryid) # go to scan courses on category (but not parent)

# Create course with ws
def create_courses(courses_to_create):
    for i_courses_to_create in courses_to_create:
        # all variables for the request
        fullname = i_courses_to_create[0]
        shortname = i_courses_to_create[0]
        categoryid = i_courses_to_create[1]
        enddate = str(timestamp_end_courses)
        startdate = str(timestamp_start_courses)
        numsections = str(numsections_courses)
        format = format_course
        
        # request 
        request_course_creation = "&courses[0][fullname]="+fullname+"&courses[0][shortname]="+shortname+"&courses[0][categoryid]="+categoryid+"&courses[0][format]="+format+"&courses[0][startdate]="+startdate+"&courses[0][enddate]="+enddate+"&courses[0][numsections]="+numsections
        webservice_course_creation = url_moodle+"/webservice/rest/server.php?wstoken="+token_ws_coursecreation+"&wsfunction="+ws_coursecreation+"&moodlewsrestformat=json"+request_course_creation
        print(webservice_course_creation)
        course_creation = requests.get(webservice_course_creation)
        webservice_reponse_content_py = json.loads(course_creation.text)   
        print(webservice_reponse_content_py) 
    
    courses_to_create = [] # reset the queue
    
    # restart on the category of the last queue element.
    get_report_courses()
    get_report_categories()
    balayage_categories(categoryid)
        
get_report_courses()
get_report_categories()
balayage_categories(0)
