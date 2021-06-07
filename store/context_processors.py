from .models import *


def get_ct_sb_for_links(reques):
    categories_for_links = Category.objects.all()
    subcategories_for_links = SubCategory.objects.all()
    return {
        'categories_for_links': categories_for_links,
        'subcategories_for_links': subcategories_for_links
    }
