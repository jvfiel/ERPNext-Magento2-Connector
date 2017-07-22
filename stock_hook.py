import frappe
from magento_lib import *



def add_stock(doc,method):

    if doc.request_from == "ERPNEXT":

        oauth = OAuth(client_key=consumer_key, client_secret=consumer_secret, resource_owner_key=access_token,
                      resource_owner_secret=access_token_secret)
        h = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        for entry in doc.items:

            # print "QTY: ",entry.qty
            # print "ACTUAL QTY: ", entry.actual_qty

            magento_id = frappe.db.sql("""SELECT magento_id FROM `tabItem` where item_code=%s""",(entry.item_code))

            if magento_id[0][0] != None:

                #NEED TO GET THE QUANTITY AFTER TRANSACTION

                item_doc = frappe.get_doc("Item",entry.item_code)

                sle_name = frappe.db.sql("""SELECT name FROM `tabStock Ledger Entry` WHERE voucher_no=%s""",(doc.name))

                print sle_name

                qty_after_transaction = frappe.db.sql("""SELECT qty_after_transaction FROM `tabStock Ledger Entry` WHERE name=%s""",(sle_name[0][0]))


                product = """
                   {
                   "product": {
                       "sku": "%s",
                       "name": "%s",
                       "attribute_set_id":4,
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
                       "extensionAttributes": {
                            "stockItem": {
                                "qty": %f,
                                "isInStock": true
                            }
                        }
                       }
                   }
                   """ % (item_doc.item_code, item_doc.item_code,
                          item_doc.disabled, item_doc, item_doc.description,
                          item_doc.description, item_doc.description,qty_after_transaction[0][0])


                print "**************** ", product
                r = requests.post(url='%s/index.php/rest/V1/products?ERPNext=true' % MAGENTO_HOST, headers=h,
                                  data=product, auth=oauth)
                print r
                print r.content

                if r.status_code == 200:
                    frappe.msgprint("""Successful. item: {1} qty is now {0}""".format(qty_after_transaction[0][0],entry.item_code))
                else:
                    frappe.throw("Unsuccessful. Status Code {0}. Response: {1}".format(r.status_code,r.content))

            else:

                frappe.throw("Item {0} has no magento_id. Trying saving the item in Item Master.".format(entry.item_code))