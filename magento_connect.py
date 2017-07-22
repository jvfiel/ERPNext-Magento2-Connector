from requests_oauthlib import OAuth1 as OAuth
import requests, json
import frappe
import base64
from magento_lib import *

def getProducts():

    oauth = OAuth(client_key=consumer_key, client_secret=consumer_secret, resource_owner_key=access_token,
                  resource_owner_secret=access_token_secret)
    h = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = requests.get(url='%s/index.php/rest/V1/products?searchCriteria=test' % MAGENTO_HOST, headers=h, auth=oauth)
    print r.content
    items = json.loads(r.content)
    print items["items"]

def postProduct(item):
    if item.request_from == "ERPNEXT":
        oauth = OAuth(client_key=consumer_key, client_secret=consumer_secret, resource_owner_key=access_token,
                      resource_owner_secret=access_token_secret)
        h = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        net_weight = item.net_weight or 0.0
        price = item.standard_rate or 0.0

        category_magento_id = frappe.db.sql("""SELECT magento_id FROM `tabItem Group` WHERE name=%s""", (item.item_group))

        category_ids = '1'

        if category_magento_id[0][0] != None:

            category_ids = category_magento_id[0][0]

        else:
            frappe.throw(
                "Item Cateogry {0} has no magento_id. Try saving Item Group in Item Group.".format(item.item_group))

        images = """  "media_gallery_entries": [ """
        test_images = ''

        photos = frappe.db.sql("""SELECT file_url,name FROM `tabFile`
                                WHERE attached_to_name=%s AND attached_to_doctype='Item' AND synced_to_erpnext=0""", (item.item_code))
        print photos

        photo_count = 0
        for photo in photos:
            with open(frappe.get_site_path() + photo[0], "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                if photo_count > 0:
                    images += """, """


                image_types = ['jpg','jpeg','png']
                image_type_is = ''

                for type in image_types:
                    if photo[0].endswith(type):
                        image_type_is = type
                        break

                if image_type_is == 'jpg':
                    image_type_is = 'jpeg'

                if image_type_is == '':
                    frappe.throw('file type not supported. Will only support the .ff:'.format(image_types))

                """

                 "media_type": "image",
                          "label": "Image",
                          "disabled": false,
                                "types": [
                                    "image",
                                    "small_image",
                                    "thumbnail"
                                ],
                          "file": "string",
                          "content": {
                          "base64_encoded_data": "%s",
                          "type": "image/png",
                          "name": "%s"


                """

                images += """
                         {
                           "media_type": "image",
                           "label": "%s",
                           "disabled": false,
                           "content": {
                             "base64_encoded_data": "%s",
                             "type": "image/%s",
                             "name": "%s"
                           }
                         }

                    """ % (photo[1],encoded_string,image_type_is,photo[1])

                test_images += """
                         {
                           "media_type": "image",
                           "label": "%s",
                           "disabled": false,
                           "content": {
                             "type": "image/%s",
                             "name": "%s"
                           }
                         }

                    """ % (photo[1],image_type_is,photo[1])
                photo_count += 1

        images += """] """

        print "Image type is: ",image_type_is
        print test_images

        product = """
        {
        "product": {
            "sku": "%s",
            "name": "%s",
            "price": %.2f,
            "attribute_set_id":4,
            "weight": %f,
            "status": %d,
             "custom_attributes": [
                {
                    "attribute_code": "category_ids",
                    "value": "%s"
                },
                {
                    "attribute_code": "description",
                    "value": "%s"
                },
                {
                    "attribute_code": "short_description",
                    "value": "%s"
                },
                {
                    "attribute_code": "meta_description",
                    "value": "%s"
                }
            ],

           %s

            }
        }
        """ % (item.item_code,item.item_code,price,net_weight,
               item.disabled,category_ids,item.description,
               item.description,item.description,images)

        exists = frappe.db.sql("""SELECT Count(*) FROM `tabItem` WHERE item_code=%s""",(item.item_code))

        r = requests.post(url='%S/index.php/rest/V1/products?ERPNext=true' % MAGENTO_HOST,headers=h,data=product,auth=oauth)

        if r.status_code == 200:
            frappe.msgprint("""Successfully updated/created item: {0} in Magento.""".format(item.item_code))
        else:
            frappe.throw("Unsuccessful. Status Code {0}. Response: {1}".format(r.status_code, r.content))

        r_magento = json.loads(r.content)

        if not item.magento_id:
            item.magento_id = r_magento['id']
        print "MAGENTO ID: ",item.magento_id
        # else:
        #     frappe.throw("""Item with item code {0} already exists in Magento. <br>Will not create. <br>Will Update.""".format(item.item_code))

        # uploadPhoto(item.item_code,oauth,h,True)

def test_uploadPhoto():
    oauth = OAuth(client_key=consumer_key, client_secret=consumer_secret, resource_owner_key=access_token,
                  resource_owner_secret=access_token_secret)
    h = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    uploadPhoto('ANOTHER TEST ITEM AA',oauth=oauth,h=h,post=True)
    #bench execute nexusapp.nexusapp.magento_connect.test_uploadPhoto

def uploadPhoto(item,oauth='',h='',post=False):

    photos = frappe.db.sql("""SELECT file_url,name FROM `tabFile`
                          WHERE attached_to_name=%s AND attached_to_doctype='Item' AND synced_to_erpnext=0""",(item))
    print photos

    for photo in photos:
        with open(frappe.get_site_path()+photo[0], "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            # print encoded_string

            if post:
                print photo[0]
                product = """
                  {
                      "entry": {
                      "media_type": "image",
                      "label": "Image",
                      "disabled": false,
                            "types": [
                                "image",
                                "small_image",
                                "thumbnail"
                            ],
                      "file": "string",
                      "content": {
                      "base64_encoded_data": "%s",
                      "type": "image/png",
                      "name": "%s"
                      }
                     }
                    }
                  """ % (encoded_string,photo[1])

                r = requests.post(url='%s/index.php/rest/V1/products/%s/media' % (MAGENTO_HOST,item), headers=h, data=product,
                                  auth=oauth)
                print r
                print r.content

                if r.status_code==200:
                    frappe.db.sql("""UPDATE `tabFile` SET synced_to_erpnext=1 WHERE name=%s""",(photo[1]))
                    frappe.db.commit()

                r_magento = json.loads(r.content)


def postCategory(item):

    oauth = OAuth(client_key=consumer_key, client_secret=consumer_secret, resource_owner_key=access_token,
                  resource_owner_secret=access_token_secret)
    h = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    product = """
    {
        "category": {
            "name": "%s",
            "isActive": true
        }
    }
    """ % (item.item_group_name)

    print "**************** ", product
    r = requests.post(url='%s/index.php/rest/V1/categories' % MAGENTO_HOST,headers=h,data=product,auth=oauth)
    print r
    print r.content

    if r.status_code == 200:
        r_magento = json.loads(r.content)

        item.magento_id = r_magento['id']
        print "MAGENTO ID: ",item.magento_id

        frappe.msgprint("""Successfully added Category: {0}""".format(item.item_group_name))

    elif r.status_code == 400:
        print "STATUS 400"
        r = requests.get(url='%s/index.php/rest/V1/categories' % MAGENTO_HOST, headers=h, auth=oauth)
        # print r.content
        r_magento = json.loads(r.content)
        print r_magento

        for cat in r_magento['children_data']:
            print cat
            if cat['name'] == item.name:
                item.magento_id = cat['id']

        frappe.msgprint("""Category {0} already exists.""".format(item.item_group_name))

