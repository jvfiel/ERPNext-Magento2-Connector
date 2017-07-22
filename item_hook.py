from magento_connect import postProduct,postCategory


def add_to_magento(doc,method):
    postProduct(doc)

def add_category(doc,method):
    postCategory(doc)