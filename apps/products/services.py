from django.db.models import F
from django.db import transaction
from django.core.cache import cache
from apps.orders.models import Order
from .models import Category

def reduce_order_stock(order: Order):
    """
    Reduces stock for all products in the order using atomic updates.
    """
    with transaction.atomic():
        for item in order.items.all():
            if item.product:
                # Use F expression to avoid race conditions
                item.product.stock = F('stock') - item.quantity
                item.product.save(update_fields=['stock'])

def get_category_tree():
    """
    Retrieves the category tree using DFS and caches it.
    """
    cache_key = 'category_tree'
    cached_tree = cache.get(cache_key)
    
    if cached_tree:
        return cached_tree
    
    # Fetch all categories
    categories = Category.objects.all()
    
    # Build adjacency list
    adj_list = {}
    roots = []
    
    for cat in categories:
        if cat.parent_id:
            if cat.parent_id not in adj_list:
                adj_list[cat.parent_id] = []
            adj_list[cat.parent_id].append(cat)
        else:
            roots.append(cat)
            
    # DFS Traversal
    def dfs(node):
        tree_node = {
            'id': node.id,
            'name': node.name,
            'slug': node.slug,
            'children': []
        }
        
        if node.id in adj_list:
            for child in adj_list[node.id]:
                tree_node['children'].append(dfs(child))
        
        return tree_node

    tree = [dfs(root) for root in roots]
    
    # Cache for 1 hour
    cache.set(cache_key, tree, 3600)
    
    return tree

